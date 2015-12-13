from durator.common.crypto.session_cipher import SessionCipher
from durator.world.opcodes import OpCode
from pyshgck.format import dump_data


class WorldPacket(object):

    # This static packet buffer ensures that all world packets are correctly
    # received in their entirety.
    _PACKET_BUF = b""

    def __init__(self, data = None):
        # self.length = 0
        self.opcode = None
        self.data = data or b""

    @staticmethod
    def from_socket(socket, session_cipher = None):
        """ Receive a WorldPacket through socket, or None if the connection is
        closed during reception. """
        packet = WorldPacket()
        while True:
            # Receive data as long as the connection is opened.
            data_part = socket.recv(1024)
            if not data_part:
                return None
            WorldPacket._PACKET_BUF += data_part

            # Continue receiving data until we have a complete header.
            if len(WorldPacket._PACKET_BUF) < SessionCipher.DECRYPT_HEADER_SIZE:
                continue

            # If a session cipher is provided, use it to decrypt the header.
            if session_cipher is not None:
                decrypted = session_cipher.decrypt(WorldPacket._PACKET_BUF)
                WorldPacket._PACKET_BUF = decrypted

            packet_size = int.from_bytes(WorldPacket._PACKET_BUF[0:2], "big")
            WorldPacket._PACKET_BUF = WorldPacket._PACKET_BUF[2:]

            # Now that we have a packet size, wait until we have all the data
            # of this packet.
            if len(WorldPacket._PACKET_BUF) < packet_size:
                continue

            # When all the packet is in the static buffer, cut it from the
            # buffer and return it.
            data = WorldPacket._PACKET_BUF[:packet_size]
            WorldPacket._PACKET_BUF = WorldPacket._PACKET_BUF[packet_size:]
            break

        print(dump_data(data), end = "")
        # packet.length = packet_size
        opcode_bytes, data = data[0:4], data[4:]
        opcode_value = int.from_bytes(opcode_bytes, "little")
        packet.opcode = OpCode(opcode_value)
        packet.data = data
        return packet
    # def compute_length(self):
    #     self.length = self.OUTGOING_OPCODE_BIN.size + len(self.data)