package test;

import java.nio.ByteBuffer;

public class Test {

	public static void main(String[] args) {
		encodeLong();
		encodeInt();
		decodeLong();
	}

	public static Long encode1() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD, (byte) 0xEF, 0x12};

		Long l = null;
		String s = new String(stream);
		l = new Long(Long.decode("0xABCDEF12"));
		System.out.print(l);
		return l;
	}

	public static Long encode2() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD, (byte) 0xEF, 0x12};

		ByteBuffer buffer = ByteBuffer.allocate(4);
		Integer i = buffer.put(stream).getInt(0);
		Long l = (long) i;
		l &= 0x00000000FFFFFFFFL;
		System.out.print(l);
		return l;
	}

	public static Long encodeLong() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD, (byte) 0xEF, 0x12}; // 2882400018

		Long l = ByteBuffer.allocate(4).put(stream).getInt(0) & 0x00000000FFFFFFFFL;

		System.out.println(l);
		return l;
	}

	public static Integer encodeInt() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD};	// 43981

		Integer i = ByteBuffer.allocate(2).put(stream).getShort(0) & 0x0000FFFF;

		System.out.println(i);
		return i;
	}

	public static byte[] decodeLong() {
		Long l = 2882400018L;

		Integer i = l.intValue();

		byte[] buf = ByteBuffer.allocate(4).putInt(i).array();
		for (int j = 0; j < 4; j++) {
			System.out.print(String.format("%02X", buf[j]) + ' ');
		}
		return buf;
	}
}