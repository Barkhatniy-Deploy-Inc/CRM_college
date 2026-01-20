package parser

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/xuri/excelize/v2"
)

type ScheduleEntry struct {
	GroupName  string
	Date       string // DD.MM.YYYY
	DayOfWeek  int
	TimeSlot   string // HH:MM-HH:MM
	PairNumber int
	Subject    string
	Teacher    string
	Auditorium string
	SheetName  string
}

// Day mapping
var dayNamesRussian = map[string]int{
	"ПОНЕДЕЛЬНИК": 1, "пн": 1,
	"ВТОРНИК": 2, "вт": 2,
	"СРЕДА": 3, "ср": 3,
	"ЧЕТВЕРГ": 4, "чт": 4,
	"ПЯТНИЦА": 5, "пт": 5,
	"СУББОТА": 6, "сб": 6,
	"ВОСКРЕСЕНЬЕ": 7, "вс": 7,
}

func ParseExcelSchedule(filePath string) ([]ScheduleEntry, error) {
	f, err := excelize.OpenFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer f.Close()

	var entries []ScheduleEntry

	for _, sheetName := range f.GetSheetList() {
		if strings.ToUpper(sheetName) == "ЗВОНКИ" {
			continue
		}

		rows, err := f.GetRows(sheetName)
		if err != nil {
			continue
		}

		// Extract groups header (Row 6 -> index 5)
		groupsInfo := extractGroupsHeader(rows)
		if len(groupsInfo) == 0 {
			continue
		}

		sheetEntries := parseSheetContent(rows, groupsInfo, sheetName)
		entries = append(entries, sheetEntries...)
	}

	return entries, nil
}

type groupInfo struct {
	name     string
	colGroup int // 0-indexed column index
	colRoom  int
}

func extractGroupsHeader(rows [][]string) []groupInfo {
	if len(rows) < 6 {
		return nil
	}
	headerRow := rows[5] // Row 6
	var groups []groupInfo

	// Start from column 4 (index 4) (Python code said 4)
	// Python: [0]=empty, [1]=Date, [2]=Class, [3]=Time, [4]=Group1...
	i := 4
	for i < len(headerRow) {
		groupName := strings.TrimSpace(headerRow[i])

		// Regex to check if it's a group name (contains letters and digits, no 'ауд')
		// Python: re.search(r'[А-ЯЁ].*\d', group_name) and 'ауд' not in group_name.lower()
		matched, _ := regexp.MatchString(`[А-Яа-яЁё].*\d`, groupName)
		if matched && !strings.Contains(strings.ToLower(groupName), "ауд") {
			info := groupInfo{
				name:     groupName,
				colGroup: i,
				colRoom:  -1,
			}
			if i+1 < len(headerRow) {
				info.colRoom = i + 1
			}
			groups = append(groups, info)
			i += 2
		} else {
			i++
		}
	}
	return groups
}

func parseSheetContent(rows [][]string, groups []groupInfo, sheetName string) []ScheduleEntry {
	var entries []ScheduleEntry
	var currentDateStr string
	var currentDayOfWeek int

	// Start from row 7 (index 6)
	for r := 6; r < len(rows); r++ {
		row := rows[r]
		if len(row) < 2 {
			continue
		}

		col1Text := strings.TrimSpace(row[1]) // Column 1 (B)

		// Check for day of week
		dayMatch := extractDayOfWeek(col1Text)
		if dayMatch != nil {
			currentDayOfWeek = dayMatch.dayNum
			currentDateStr = dayMatch.dateStr
			continue
		}

		if currentDateStr != "" && currentDayOfWeek != 0 {
			timeSlot := extractTimeSlot(row)
			pairNum := extractPairNumber(row)

			if timeSlot != "" {
				for _, info := range groups {
					if info.colGroup >= len(row) {
						continue
					}

					subjectAndTeacher := strings.TrimSpace(row[info.colGroup])
					room := ""
					if info.colRoom != -1 && info.colRoom < len(row) {
						room = strings.TrimSpace(row[info.colRoom])
					}

					if subjectAndTeacher != "" && subjectAndTeacher != "-" {
						subject, teacher := parseSubjectAndTeacher(subjectAndTeacher)
						entries = append(entries, ScheduleEntry{
							GroupName:  info.name,
							Date:       currentDateStr,
							DayOfWeek:  currentDayOfWeek,
							TimeSlot:   timeSlot,
							PairNumber: pairNum,
							Subject:    subject,
							Teacher:    teacher,
							Auditorium: room,
							SheetName:  sheetName,
						})
					}
				}
			}
		}
	}
	return entries
}

type dayData struct {
	dayNum  int
	dateStr string
}

func extractDayOfWeek(text string) *dayData {
	for name, num := range dayNamesRussian {
		if strings.HasPrefix(strings.ToLower(text), strings.ToLower(name)) {
			// Regex find date DD.MM.YYYY
			re := regexp.MustCompile(`(\d{2}\.\d{2}\.\d{4})`)
			match := re.FindString(text)
			if match != "" {
				return &dayData{dayNum: num, dateStr: match}
			}
		}
	}
	return nil
}

func extractTimeSlot(row []string) string {
	if len(row) > 3 {
		timeStr := strings.TrimSpace(row[3])
		matched, _ := regexp.MatchString(`\d{2}:\d{2}-\d{2}:\d{2}`, timeStr)
		if matched {
			return timeStr
		}
	}
	return ""
}

func extractPairNumber(row []string) int {
	if len(row) > 2 {
		val, err := strconv.Atoi(row[2])
		if err == nil && val > 0 && val <= 8 {
			return val
		}
	}
	return 0
}

func parseSubjectAndTeacher(text string) (string, string) {
	// Format: "Subject Teacher I.O."
	// Regex for teacher: space + Capital + lowercase + space + Capital. + Capital.
	re := regexp.MustCompile(`\s([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.)`)
	loc := re.FindStringIndex(text)

	if loc != nil {
		teacher := strings.TrimSpace(text[loc[0]:])
		subject := strings.TrimSpace(text[:loc[0]])
		return subject, teacher
	}

	return text, ""
}
