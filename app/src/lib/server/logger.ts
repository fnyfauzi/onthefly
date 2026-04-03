import winston from "winston";
import DailyRotateFile from "winston-daily-rotate-file";
const { combine, timestamp, printf, colorize, align } = winston.format;

// https://betterstack.com/community/guides/logging/how-to-install-setup-and-use-winston-and-morgan-to-log-node-js-applications/
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: combine(
    // colorize({ all: true }),
    timestamp({ format: "YYYY-MM-DD hh:mm:ss" }),
    // align(),
    // printf((info) => `[${info.timestamp}] ${info.level}: ${info.message}`)
    printf((info) => `[${info.timestamp}]: ${info.message}`)
  ),
  transports: [
    new winston.transports.Console(),
    new DailyRotateFile({
      filename: "logs/debug.log",
      dirname: 'logs',
      createSymlink: true,
      symlinkName: 'debug.log',
      handleExceptions: true,
      datePattern: "YYYY-MM-DD",
      maxSize: '20m', // max before rotate (optional)
      maxFiles: "14d", // Keep for 14 days (optional)
      json: false,
    }),
  ],
});

export default logger;
