from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, model_validator

from pycricinfo.source_models.api.common import CCBaseModel


class BowlingDetailsToHand(CCBaseModel):
    balls: int
    wickets: int
    economy_rate: float
    conceded: int


class PitchMapElement(BaseModel):
    runs: int
    wickets: int
    balls: int


class PitchMapLength(BaseModel):
    wide_outside_off: PitchMapElement
    outside_off: PitchMapElement
    straight: PitchMapElement
    outside_leg: PitchMapElement
    wide_outside_leg: PitchMapElement


class PitchMap(BaseModel):
    full_toss: PitchMapLength
    yorker: PitchMapLength
    full: PitchMapLength
    good: PitchMapLength
    short_of_good: PitchMapLength
    short: PitchMapLength


class BowlingDetails(CCBaseModel):
    active: bool
    active_name: str
    order: int
    overall_lhb: Optional[BowlingDetailsToHand] = None
    overall_rhb: Optional[BowlingDetailsToHand] = None
    pitch_map_lhb_raw: Optional[list[list[list[int]]]] = Field(
        default=None, validation_alias=AliasChoices("pitch_map_lhb_raw", "pitchMapLhb")
    )
    pitch_map_rhb_raw: Optional[list[list[list[int]]]] = Field(
        default=None, validation_alias=AliasChoices("pitch_map_rhb_raw", "pitchMapRhb")
    )
    pitch_map_right: Optional[PitchMap] = None
    pitch_map_left: Optional[PitchMap] = None

    @model_validator(mode="before")
    @classmethod
    def generate_structured_pitch_maps(cls, data: dict):
        pitch_map_length_fields = PitchMapLength.model_fields.keys()
        pitch_map_fields = PitchMap.model_fields.keys()

        pitchMapRhb = data.get("pitchMapRhb", None)
        if pitchMapRhb:
            data["pitchMapRight"] = cls._generate_pitch_map(pitch_map_fields, pitch_map_length_fields, pitchMapRhb)

        pitchMapLhb = data.get("pitchMapLhb", None)
        if pitchMapLhb:
            data["pitchMapLeft"] = cls._generate_pitch_map(pitch_map_fields, pitch_map_length_fields, pitchMapLhb)
        return data

    def _generate_pitch_map(
        pitch_map_fields: list[str], pitch_map_length_fields: list[str], raw_pitch_map_data: list[list[list[int]]]
    ):
        lengths = []
        for length in raw_pitch_map_data:
            lines = []
            for line in length:
                element = PitchMapElement(runs=line[0], wickets=line[1], balls=line[2])
                lines.append(element)

            line_data = dict(zip(pitch_map_length_fields, lines))
            length_map = PitchMapLength(**line_data)
            lengths.append(length_map)

        length_data = dict(zip(pitch_map_fields, lengths))
        return PitchMap(**length_data)
