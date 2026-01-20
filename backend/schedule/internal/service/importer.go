package service

import (
	"context"
	"fmt"
	"log"
	prisma "schedule/db"
	"schedule/internal/db"
	"schedule/internal/parser"
	"strings"
	"time"
)

type ImportStats struct {
	Status             string   `json:"status"`
	Message            string   `json:"message"`
	GroupsCreated      int      `json:"groups_created"`
	GroupsUpdated      int      `json:"groups_updated"`
	AuditoriumsCreated int      `json:"auditoriums_created"`
	SlotsCreated       int      `json:"slots_created"`
	SlotsUpdated       int      `json:"slots_updated"`
	Errors             []string `json:"errors"`
}

type ScheduleImporter struct {
	client *prisma.PrismaClient
	ctx    context.Context
}

func NewScheduleImporter() *ScheduleImporter {
	return &ScheduleImporter{
		client: db.GetClient(),
		ctx:    context.Background(),
	}
}

func (s *ScheduleImporter) ImportSchedule(filePath string) ImportStats {
	stats := ImportStats{
		Status: "success",
		Errors: []string{},
	}

	entries, err := parser.ParseExcelSchedule(filePath)
	if err != nil {
		stats.Status = "error"
		stats.Message = fmt.Sprintf("Failed to parse file: %v", err)
		stats.Errors = append(stats.Errors, stats.Message)
		return stats
	}

	if len(entries) == 0 {
		stats.Status = "error"
		stats.Message = "File is empty or contains no data"
		return stats
	}

	for _, entry := range entries {
		if err := s.processEntry(entry, &stats); err != nil {
			msg := fmt.Sprintf("Error processing entry %v: %v", entry, err)
			stats.Errors = append(stats.Errors, msg)
			log.Println(msg)
		}
	}

	stats.Message = fmt.Sprintf("Import completed. Groups: %d, Slots: %d, Errors: %d", stats.GroupsCreated, stats.SlotsCreated, len(stats.Errors))
	return stats
}

func (s *ScheduleImporter) processEntry(entry parser.ScheduleEntry, stats *ImportStats) error {
	// 1. Group
	group, created, err := s.getOrCreateGroup(entry.GroupName)
	if err != nil {
		return err
	}
	if created {
		stats.GroupsCreated++
	} else {
		stats.GroupsUpdated++
	}

	// 2. Auditorium
	var auditorium *prisma.AuditoriumModel
	if entry.Auditorium != "" {
		aud, created, err := s.getOrCreateAuditorium(entry.Auditorium)
		if err != nil {
			return err
		}
		auditorium = aud
		if created {
			stats.AuditoriumsCreated++
		}
	}

	// 3. Time
	start, end, err := s.parseDateTime(entry.Date, entry.TimeSlot)
	if err != nil {
		return err
	}

	// 4. Slot
	created, err = s.createOrUpdateSlot(group, auditorium, entry, start, end)
	if err != nil {
		return err
	}
	if created {
		stats.SlotsCreated++
	} else {
		stats.SlotsUpdated++
	}

	return nil
}

func (s *ScheduleImporter) getOrCreateGroup(name string) (*prisma.GroupModel, bool, error) {
	// Check if exists
	group, err := s.client.Group.FindFirst(
		prisma.Group.Name.Equals(name),
	).Exec(s.ctx)

	if err == nil {
		return group, false, nil
	}

	// Create
	newGroup, err := s.client.Group.CreateOne(
		prisma.Group.Name.Set(name),
		prisma.Group.Description.Set(fmt.Sprintf("Группа %s", name)),
	).Exec(s.ctx)
	if err != nil {
		return nil, false, err
	}
	return newGroup, true, nil
}

func (s *ScheduleImporter) getOrCreateAuditorium(name string) (*prisma.AuditoriumModel, bool, error) {
	aud, err := s.client.Auditorium.FindUnique(
		prisma.Auditorium.Name.Equals(name),
	).Exec(s.ctx)

	if err == nil {
		return aud, false, nil
	}

	newAud, err := s.client.Auditorium.CreateOne(
		prisma.Auditorium.Name.Set(name),
		prisma.Auditorium.Description.Set(fmt.Sprintf("Аудитория %s", name)),
	).Exec(s.ctx)
	if err != nil {
		return nil, false, err
	}
	return newAud, true, nil
}

func (s *ScheduleImporter) parseDateTime(dateStr, timeSlot string) (time.Time, time.Time, error) {
	// dateStr: DD.MM.YYYY
	// timeSlot: HH:MM-HH:MM
	date, err := time.Parse("02.01.2006", dateStr)
	if err != nil {
		return time.Time{}, time.Time{}, fmt.Errorf("invalid date format: %v", err)
	}

	times := strings.Split(timeSlot, "-")
	if len(times) != 2 {
		return time.Time{}, time.Time{}, fmt.Errorf("invalid time slot format: %s", timeSlot)
	}

	startT, err := time.Parse("15:04", strings.TrimSpace(times[0]))
	if err != nil {
		return time.Time{}, time.Time{}, err
	}
	endT, err := time.Parse("15:04", strings.TrimSpace(times[1]))
	if err != nil {
		return time.Time{}, time.Time{}, err
	}

	start := time.Date(date.Year(), date.Month(), date.Day(), startT.Hour(), startT.Minute(), 0, 0, time.Local)
	end := time.Date(date.Year(), date.Month(), date.Day(), endT.Hour(), endT.Minute(), 0, 0, time.Local)

	return start, end, nil
}

func (s *ScheduleImporter) createOrUpdateSlot(
	group *prisma.GroupModel,
	auditorium *prisma.AuditoriumModel,
	entry parser.ScheduleEntry,
	start, end time.Time,
) (bool, error) {

	// Check existing slot
	existing, err := s.client.ClassSlot.FindFirst(
		prisma.ClassSlot.GroupID.Equals(group.ID),
		prisma.ClassSlot.StartTime.Equals(start),
		prisma.ClassSlot.EndTime.Equals(end),
		prisma.ClassSlot.Title.Equals(entry.Subject),
	).Exec(s.ctx)

	if err == nil {
		// Update
		// In Go Prisma, updates are separate calls usually.
		_, err := s.client.ClassSlot.FindUnique(
			prisma.ClassSlot.ID.Equals(existing.ID),
		).Update(
			prisma.ClassSlot.Instructor.Set(entry.Teacher),
			// Link auditorium if present
			// Note: If auditorium is nil, we might want to unset it, but optional unset isn't always straightforward.
			// Assuming we just update if we have a new one or keep old.
			// Logic: verify if we need to update auditorium.
		).Exec(s.ctx)

		// If auditorium provided, update it separately to avoid nil issues in chain if possible, or use proper Set
		if auditorium != nil {
			_, err = s.client.ClassSlot.FindUnique(
				prisma.ClassSlot.ID.Equals(existing.ID),
			).Update(
				prisma.ClassSlot.AuditoriumID.Set(auditorium.ID),
			).Exec(s.ctx)
		}

		return false, err
	}

	// Create
	optionalAud := prisma.ClassSlot.AuditoriumID.SetOptional(nil)
	if auditorium != nil {
		optionalAud = prisma.ClassSlot.AuditoriumID.Set(auditorium.ID)
	}

	_, err = s.client.ClassSlot.CreateOne(
		prisma.ClassSlot.Title.Set(entry.Subject),
		prisma.ClassSlot.StartTime.Set(start),
		prisma.ClassSlot.EndTime.Set(end),
		prisma.ClassSlot.Group.Link(prisma.Group.ID.Equals(group.ID)),
		optionalAud,
		prisma.ClassSlot.Instructor.Set(entry.Teacher),
		prisma.ClassSlot.Status.Set(prisma.SlotStatusScheduled),
	).Exec(s.ctx)

	if err != nil {
		return false, err
	}
	return true, nil
}
