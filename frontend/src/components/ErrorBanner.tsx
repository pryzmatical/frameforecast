interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      data-testid="error-banner"
      className="flex flex-col gap-2 rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300 sm:flex-row sm:items-center sm:justify-between"
    >
      <span>{message}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="self-start rounded-md border border-red-400/40 px-3 py-1 text-xs text-red-200 hover:bg-red-500/20 sm:self-auto"
        >
          Retry
        </button>
      )}
    </div>
  );
}
