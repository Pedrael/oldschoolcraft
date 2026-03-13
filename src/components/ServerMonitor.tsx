import { useEffect } from "react";
import { Refresh } from "@mui/icons-material";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import {
  useGetServerInfo,
  type McStatusResponse,
} from "../hooks/useGetServerInfo";

type StatusIndicatorProps = {
  online: boolean;
};

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ online }) => {
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      width={20}
      height={20}
      borderRadius="50%"
      sx={{
        border: (theme) =>
          `2px solid ${online ? theme.palette.success.light : theme.palette.error.light}`,
        backgroundColor: (theme) =>
          online ? theme.palette.success.light : theme.palette.error.light,
        boxShadow: (theme) =>
          online ? theme.palette.success.dark : theme.palette.error.dark,
      }}
    ></Box>
  );
};

type InfoRowProps = {
  label: string;
  value?: React.ReactNode;
  children?: React.ReactNode;
};

const InfoRow: React.FC<InfoRowProps> = ({ label, value, children }) => {
  return (
    <Box
      display="flex"
      justifyContent="space-between"
      gap={2}
      py={0.75}
      sx={{
        borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
      }}
    >
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography
        variant="body2"
        sx={{
          textAlign: "right",
          wordBreak: "break-word",
        }}
      >
        {value}
      </Typography>
      {children}
    </Box>
  );
};

function formatTimestamp(timestamp?: number): string {
  if (!timestamp) return "Unknown";

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Unknown";

  return date.toLocaleString();
}

function formatRelativeTime(timestamp?: number): string {
  if (!timestamp) return "Unknown";

  const diffMs = Date.now() - timestamp;
  const diffSec = Math.max(0, Math.floor(diffMs / 1000));

  if (diffSec < 5) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;

  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;

  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;

  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

type ServerStatusCardProps = {
  serverInfo: McStatusResponse;
  onRefresh: () => void;
  isRefreshing?: boolean;
};

const ServerStatusCard: React.FC<ServerStatusCardProps> = ({
  serverInfo,
  onRefresh,
  isRefreshing = false,
}) => {
  const isOnline = serverInfo.online;
  const hostLabel = `${serverInfo.host}:${serverInfo.port}`;
  const playersLabel = `${serverInfo.players.online} / ${serverInfo.players.max}`;
  const updatedAtLabel = formatRelativeTime(serverInfo.retrieved_at);
  const updatedAtFull = formatTimestamp(serverInfo.retrieved_at);

  return (
    <Paper
      elevation={0}
      sx={{
        width: "100%",
        maxWidth: 460,
        p: 3,
        borderRadius: 0,
        backgroundColor: "background.paper",
        border: "2px solid",
        borderColor: isOnline ? "success.dark" : "error.dark",
      }}
    >
      <Stack spacing={2.5}>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          gap={2}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <StatusIndicator online={isOnline} />
            <Box ml={1}>
              <Typography
                variant="h6"
                sx={{ textAlign: "left", mb: 0.5, textIndent: "0" }}
              >
                Server Status
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: isOnline ? "success.light" : "error.light",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  textIndent: "0",
                }}
              >
                {isOnline ? "Online" : "Offline"}
              </Typography>
            </Box>
          </Box>

          <Button
            onClick={onRefresh}
            disabled={isRefreshing}
            variant="outlined"
            startIcon={
              isRefreshing ? (
                <CircularProgress size={16} color="inherit" />
              ) : (
                <Refresh />
              )
            }
            sx={{
              minWidth: 0,
              borderRadius: 0,
              whiteSpace: "nowrap",
            }}
          >
            Refresh
          </Button>
        </Box>

        <Box>
          <InfoRow label="Host" value={hostLabel} />
          <InfoRow label="Players" value={playersLabel} />
          <InfoRow label="Last update">
            <Box>
              <Typography variant="body2" component="div">
                {updatedAtLabel}
              </Typography>
              <Typography
                variant="caption"
                component="div"
                color="text.secondary"
              >
                {updatedAtFull}
              </Typography>
            </Box>
          </InfoRow>
        </Box>
      </Stack>
    </Paper>
  );
};

type ServerErrorCardProps = {
  message: string;
  onRefresh: () => void;
  isRefreshing?: boolean;
};

const ServerErrorCard: React.FC<ServerErrorCardProps> = ({
  message,
  onRefresh,
  isRefreshing = false,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        width: "100%",
        maxWidth: 460,
        p: 3,
        borderRadius: 0,
        backgroundColor: "background.paper",
        border: "2px solid",
        borderColor: (theme) => theme.palette.error.dark,
      }}
    >
      <Stack spacing={2} alignItems="center">
        <Box display="flex" alignItems="center" gap={1.5}>
          <StatusIndicator online={false} />
          <Box>
            <Typography
              variant="h6"
              sx={{ textAlign: "left", mb: 0.5, textIndent: "0" }}
            >
              Server Status
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: (theme) => theme.palette.error.light,
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                textIndent: "0",
              }}
            >
              Request failed
            </Typography>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>

        <Box>
          <Button
            onClick={onRefresh}
            disabled={isRefreshing}
            variant="outlined"
            startIcon={
              isRefreshing ? (
                <CircularProgress size={16} color="inherit" />
              ) : (
                <Refresh />
              )
            }
            sx={{ borderRadius: 0 }}
          >
            Refresh
          </Button>
        </Box>
      </Stack>
    </Paper>
  );
};

export const ServerMonitor: React.FC = () => {
  const { serverInfo, isLoading, error, fetchServerInfo } =
    useGetServerInfo("5.58.187.169:25565");
  useEffect(() => {
    fetchServerInfo();
  }, [fetchServerInfo]);

  return (
    <Box display="flex" justifyContent="center" width="100%">
      {isLoading && !serverInfo ? (
        <Paper
          elevation={0}
          sx={{
            width: "100%",
            maxWidth: 460,
            p: 3,
            borderRadius: 0,
            backgroundColor: "background.paper",
            border: "2px solid",
            borderColor: "primary.dark",
          }}
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <CircularProgress size={24} />
            <Typography variant="body1">Fetching server status...</Typography>
          </Stack>
        </Paper>
      ) : error ? (
        <ServerErrorCard
          message={error.message}
          onRefresh={fetchServerInfo}
          isRefreshing={isLoading}
        />
      ) : serverInfo ? (
        <ServerStatusCard
          serverInfo={serverInfo}
          onRefresh={fetchServerInfo}
          isRefreshing={isLoading}
        />
      ) : null}
    </Box>
  );
};
