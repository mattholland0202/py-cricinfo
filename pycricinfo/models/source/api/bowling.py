from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, model_validator

from pycricinfo.models.source.api.common import CCBaseModel


class BowlingDetailsToHand(CCBaseModel):
    deliveries: int = Field(validation_alias=AliasChoices("deliveries", "balls"))
    wickets: int
    economy_rate: float
    conceded: int


class PitchMapElement(BaseModel):
    runs: int
    wickets: int
    deliveries: int


class PitchMapLines(BaseModel):
    wide_outside_off: PitchMapElement
    outside_off: PitchMapElement
    straight: PitchMapElement
    outside_leg: PitchMapElement
    wide_outside_leg: PitchMapElement


class PitchMapLengths(BaseModel):
    full_toss: PitchMapLines
    yorker: PitchMapLines
    full: PitchMapLines
    good: PitchMapLines
    short_of_good: PitchMapLines
    short: PitchMapLines


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
    pitch_map_right: Optional[PitchMapLengths] = None
    pitch_map_left: Optional[PitchMapLengths] = None

    @model_validator(mode="before")
    @classmethod
    def generate_structured_pitch_maps(cls, data: dict) -> dict:
        """
        Convert the unstructured pitch map data into a more fully described entity, with structured
        fields for delivery data for each line and length

        Parameters
        ----------
        data : dict
            The raw fata for a bowling innings

        Returns
        -------
        dict
            The data with the new structured fields added
        """
        pitch_map_line_fields = PitchMapLines.model_fields.keys()
        pitch_map_length_fields = PitchMapLengths.model_fields.keys()

        pitchMapRhb = data.get("pitchMapRhb", None)
        if pitchMapRhb:
            data["pitchMapRight"] = cls._generate_pitch_map(pitch_map_length_fields, pitch_map_line_fields, pitchMapRhb)

        pitchMapLhb = data.get("pitchMapLhb", None)
        if pitchMapLhb:
            data["pitchMapLeft"] = cls._generate_pitch_map(pitch_map_length_fields, pitch_map_line_fields, pitchMapLhb)
        return data

    def _generate_pitch_map(
        pitch_map_length_fields: list[str], pitch_map_line_fields: list[str], raw_pitch_map_data: list[list[list[int]]]
    ) -> PitchMapLengths:
        """
        Take the names of each bowling length and line, and zip them together with the raw data to create an
        enriched entity

        Parameters
        ----------
        pitch_map_length_fields : list[str]
            The names of each length for pitch map data, in order
        pitch_map_line_fields : list[str]
            The names of each line for pitch map data, in order
        raw_pitch_map_data : list[list[list[int]]]
            The raw data to enrich for this pitch map

        Returns
        -------
        PitchMapLengths
            The enriched pitch map data
        """
        lengths = []
        for length in raw_pitch_map_data:
            lines = []
            for line in length:
                element = PitchMapElement(runs=line[0], wickets=line[1], deliveries=line[2])
                lines.append(element)

            line_data = dict(zip(pitch_map_line_fields, lines))
            length_map = PitchMapLines(**line_data)
            lengths.append(length_map)

        length_data = dict(zip(pitch_map_length_fields, lengths))
        return PitchMapLengths(**length_data)
