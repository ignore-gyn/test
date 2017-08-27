package test;

import java.nio.ByteBuffer;

public class Test {

	public static void main(String[] args) {
		encodeLong();
		encodeInt();
		decodeLong();
	}

	public static Long encodeLong1() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD, (byte) 0xEF, 0x12}; // 2882400018


		ByteBuffer buf = ByteBuffer.allocate(4).put(stream);
		// int & long
		// (long)int & long
		// (long)-23 = -23L
		Long l = -4L;
//		Long l = buf.getInt(0) & 0x7FFFFFFFFFFFFFFFL;
//		long l = buf.getInt(0) | 0x0000000000000000L;

		Long l1 = (long) ByteBuffer.allocate(4).put(stream).getInt(0);
		Long l2 = ByteBuffer.allocate(8).putInt(0).put(stream).getLong(0);

		System.out.println(Integer.toBinaryString(buf.getInt(0)));
		System.out.println(Long.toBinaryString(l));
		System.out.println(l);
		System.out.println(l1);
		System.out.println(l2);
		return l;
	}

	public static Long encodeLong() {
		byte[] stream = {(byte) 0xAB, (byte) 0xCD, (byte) 0xEF, 0x12}; // 2882400018


		Long l = ByteBuffer.allocate(8).putInt(0).put(stream).getLong(0);
//		Long l = ByteBuffer.allocate(4).put(stream).getInt(0) & 0x00000000FFFFFFFFL;

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

		byte[] buf = ByteBuffer.allocate(4).putInt(l.intValue()).array();
//		for (int j = 0; j < 4; j++) {
//			System.out.print(String.format("%02X", buf[j]) + ' ');
//		}
		return buf;
	}
}