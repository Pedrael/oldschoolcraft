import { useCallback, useState } from "react";

export type McStatusResponse = {
  online: boolean;
  host: string;
  port: number;
  ip_address: string;
  eula_blocked: boolean;
  retrieved_at: number;
  expires_at: number;
  srv_record: string | null;
  version: McStatusVersion;
  players: McStatusPlayers;
  motd: McStatusMotd;
  icon: string | null;
  mods: McStatusMod[];
  software: string | null;
  plugins: McStatusPlugin[];
};

export type McStatusVersion = {
  name_raw: string;
  name_clean: string;
  name_html: string;
  protocol: number;
};

export type McStatusPlayers = {
  online: number;
  max: number;
  list: string[];
};

export type McStatusMotd = {
  raw: string;
  clean: string;
  html: string;
};

export type McStatusMod = {
  name: string;
  version: string;
};

export type McStatusPlugin = {
  name?: string;
  version?: string;
};

export const useGetServerInfo = (address: string) => {
  const [serverInfo, setServerInfo] = useState<McStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const fetchServerInfo = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(
        `https://api.mcstatus.io/v2/status/java/${address}`,
      );
      const data = await response.json();
      setServerInfo(data);
    } catch (error) {
      setError(error as Error);
    } finally {
      setIsLoading(false);
    }
  }, [address]);
  return { serverInfo, isLoading, error, fetchServerInfo };
};
