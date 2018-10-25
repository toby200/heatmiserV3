from heatmiserV3.config import Config
from heatmiserV3.field import Field


class Protocol:
    def __init__(self, device_id, protocol):
        self.device_id = device_id
        self.field_map, self.offset_map, self.dcb_map = self._create_maps(protocol)

    @staticmethod
    def _create_maps(protocol):
        offset_map = {}
        field_map = {}
        dcb_map = {}

        for indices, field in protocol['fields'].items():
            (field_address, dcb_index) = map(int, indices.split(","))
            if isinstance(field, dict):
                field_name = field[Config.NAME]
                field_type = field['type']
                field_obj = Field(field_address, dcb_index, field_name, field_type)
            else:
                field_name = field
                field_obj = Field(field_address, dcb_index, field, Config.BASIC_FIELD)
            offset_map[indices] = field_obj
            field_map[field_name] = field_obj
            dcb_map[dcb_index] = field_obj
        return field_map, offset_map, dcb_map

    def get_field(self, lookup):
        if isinstance(lookup, str):
            result = self.field_map.get(lookup)
        elif isinstance(lookup, int):
            result = self.offset_map.get(lookup)
        else:
            raise ValueError("Lookup must be an integer offset or field name")

        if result:
            return result
        else:
            raise ValueError("Lookup failed for " + str(lookup))

    def parse_response(self, message_bytes):
        response = {}
        for dcb_index, field in self.dcb_map.items():
            if dcb_index+2 >= len(message_bytes):
                # dcb may finish early depending on program mode
                continue
            end = dcb_index+field.get_length()
            response[field.name] = field.parse_field(message_bytes[dcb_index:end])
        return response

    def __repr__(self):
        return self.device_id + ": " + str(self.offset_map)