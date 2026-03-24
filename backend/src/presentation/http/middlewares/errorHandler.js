export function errorHandler(error, _req, res, _next) {
  const isClientError = /required|invalid|not found/i.test(error.message);
  const statusCode = isClientError ? 400 : 500;

  res.status(statusCode).json({
    error: error.message,
  });
}
