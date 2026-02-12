package techcard

type StageUpdate struct {
	NomerEtapa             int    `json:"nomer_etapa"`
	NazvanieEtapa          string `json:"nazvanie_etapa"`
	CelEtapa               string `json:"cel_etapa"`
	Dlitelnost             string `json:"dlitelnost"`
	DeyatelnostPrepod      string `json:"deyatelnost_prepod"`
	DeyatelnostObuch       string `json:"deyatelnost_obuch"`
	FormiruemyeKompetencii string `json:"formiruemye_kompetencii"`
}

type TechCardUpdate struct {
	ID             int           `json:"id"`
	Tema           string        `json:"tema"`
	LessonID       int           `json:"lesson_id"`
	GroupID        int           `json:"group_id"`
	LessonTypeID   int           `json:"lesson_type_id"`
	NomerZanyatiya string        `json:"nomer_zanyatiya"`
	PedTech        string        `json:"ped_tech"`
	CelZanyatiya   string        `json:"cel_zanyatiya"`
	ZadachiObuch   string        `json:"zadachi_obuch"`
	ZadachiRazv    string        `json:"zadachi_razv"`
	ZadachiVosp    string        `json:"zadachi_vosp"`
	PrognozResult  string        `json:"prognoz_result"`
	Oborudovanie   string        `json:"oborudovanie"`
	Istochniki     string        `json:"istochniki"`
	Stages         []StageUpdate `json:"stages"`
}

type TechCardResponse struct {
	ID             int           `json:"id"`
	LessonID       int           `json:"lesson_id"`
	GroupID        int           `json:"group_id"`
	Tema           string        `json:"tema"`
	NomerZanyatiya string        `json:"nomer_zanyatiya"`
	Stages         []StageUpdate `json:"stages"`
}
