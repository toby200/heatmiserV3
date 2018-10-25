from heatmiserV3.structures import Structures
from heatmiserV3.config import Config



class Field:
    def __init__(self, address :int, dcb_index :int, name :str, field_type :str):
        self.offset = address
        self.dcb_index = dcb_index
        self.name = name
        self.field_type = field_type

    def get_length(self):
        if self.field_type == Config.BASIC_FIELD:
            return 1
        else:
            return self._get_structure_length(self.field_type)

    def parse_field(self, field_bytes):
        assert len(field_bytes) == self.get_length(), \
            "Field {} expects {} bytes not {}".format(self, self.get_length(), len(field_bytes))
        if self.field_type == Config.BASIC_FIELD:
            return int.from_bytes(field_bytes, byteorder='big')
        elif self.field_type == '2-byte':
            return int.from_bytes(field_bytes, byteorder='big')
        else:
            structure = Structures().structures.get(self.field_type)
            return self.parse_structure(structure, field_bytes)

    def parse_structure(self, structure, msg_bytes)->dict:
        parsed = {}
        for offset, entry in structure.items():
            if offset == 'length':
                continue
            if isinstance(entry, str):
                parsed[entry] = int.from_bytes(msg_bytes[offset:offset+1], byteorder='big')
            else:
                sub_structure = Structures().structures.get(entry['type'])
                sub_bytes = msg_bytes[offset:offset+sub_structure['length']]
                parsed[entry['name']] = self.parse_structure(sub_structure, sub_bytes)
        return parsed

    @staticmethod
    def _get_structure_length(structure_id):
        structure_details = Structures().structures.get(structure_id)
        if not structure_details:
            raise ValueError("Invalid structure id: " + structure_id)
        return  structure_details.get('length')

    def __repr__(self):
        return "name={}, offset={}, dcb_index={}, type={}"\
            .format(self.name, self.offset, self.dcb_index, self.field_type)