import express, { type Express } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import { createProxyMiddleware } from "http-proxy-middleware";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

// Proxy everything else to the Streamlit app on port 5000.
// Export so index.ts can attach the WS upgrade handler to the HTTP server.
export const streamlitProxy = createProxyMiddleware({
  target: "http://localhost:5000",
  changeOrigin: true,
  ws: true,
  on: {
    proxyRes(proxyRes) {
      // Strip headers that block Streamlit from loading inside Replit's iframe
      delete proxyRes.headers["x-frame-options"];
      delete proxyRes.headers["content-security-policy"];
    },
  },
});

app.use("/", streamlitProxy);

export default app;
