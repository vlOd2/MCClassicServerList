package com.mojang.minecraft.server;

import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
  Minecraft login verify patch for vanilla Minecraft Classic Servers
  Tested with c10.0.1
  Tooken from c10.0.1
*/

public final class i
{
	private String salt;

	public i(String salt)
	{
		this.salt = salt;
	}

	public final String a(String str)
	{
		try
		{
			MessageDigest algorithm = MessageDigest.getInstance("MD5");
			algorithm.update((this.salt + str).getBytes());
			String hash = (new BigInteger(1, algorithm.digest())).toString(16);
			return hash;
		}
		catch (NoSuchAlgorithmException ex)
		{
			throw new RuntimeException(ex);
		}
	}
}
