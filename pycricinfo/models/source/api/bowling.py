"""Models for a Player's bowling innings."""

from pydantic import AliasChoices, BaseModel, Field, model_validator

from pycricinfo.models.source.api.common import CCBaseModel


class BowlingDetailsToHand(CCBaseModel):
    """Bowling figures against either left- or right-handed batters."""

    deliveries: int = Field(validation_alias=AliasChoices("deliveries", "balls"))
    wickets: int
    economy_rate: float
    conceded: int


class PitchMapElement(BaseModel):
    """Runs, wickets and deliveries for one line and length on a pitch map."""

    runs: int
    wickets: int
    deliveries: int


class PitchMapLines(BaseModel):
    """Pitch map data for each line, at one length."""

    wide_outside_off: PitchMapElement
    outside_off: PitchMapElement
    straight: PitchMapElement
    outside_leg: PitchMapElement
    wide_outside_leg: PitchMapElement


class PitchMapLengths(BaseModel):
    """Pitch map data for each length, from full toss to short."""

    full_toss: PitchMapLines
    yorker: PitchMapLines
    full: PitchMapLines
    good: PitchMapLines
    short_of_good: PitchMapLines
    short: PitchMapLines


class BowlingDetails(CCBaseModel):
    """Extended details of a Player's bowling innings, including pitch maps."""

    active: bool
    active_name: str
    order: int
    overall_lhb: BowlingDetailsToHand | None = None
    overall_rhb: BowlingDetailsToHand | None = None
    pitch_map_lhb_raw: list[list[list[int]]] | None = Field(
        default=None, validation_alias=AliasChoices("pitch_map_lhb_raw", "pitchMapLhb")
    )
    pitch_map_rhb_raw: list[list[list[int]]] | None = Field(
        default=None, validation_alias=AliasChoices("pitch_map_rhb_raw", "pitchMapRhb")
    )
    pitch_map_right: PitchMapLengths | None = None
    pitch_map_left: PitchMapLengths | None = None

    @model_validator(mode="before")
    @classmethod
    def generate_structured_pitch_maps(cls, data: dict) -> dict:
        """
        Convert the unstructured pitch map data into structured fields for each line and length.

        Parameters
        ----------
        data : dict
            The raw data for a bowling innings

        Returns
        -------
        dict
            The data with the new structured fields added
        """
        pitch_map_line_fields = PitchMapLines.model_fields.keys()
        pitch_map_length_fields = PitchMapLengths.model_fields.keys()

        pitch_map_rhb = data.get("pitchMapRhb")
        if pitch_map_rhb:
            data["pitchMapRight"] = cls._generate_pitch_map(
                pitch_map_length_fields, pitch_map_line_fields, pitch_map_rhb
            )

        pitch_map_lhb = data.get("pitchMapLhb")
        if pitch_map_lhb:
            data["pitchMapLeft"] = cls._generate_pitch_map(
                pitch_map_length_fields, pitch_map_line_fields, pitch_map_lhb
            )
        return data

    @staticmethod
    def _generate_pitch_map(
        pitch_map_length_fields: list[str], pitch_map_line_fields: list[str], raw_pitch_map_data: list[list[list[int]]]
    ) -> PitchMapLengths:
        """
        Zip the names of each bowling length and line together with the raw pitch map data.

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

            line_data = dict(zip(pitch_map_line_fields, lines, strict=False))
            length_map = PitchMapLines(**line_data)
            lengths.append(length_map)

        length_data = dict(zip(pitch_map_length_fields, lengths, strict=False))
        return PitchMapLengths(**length_data)
