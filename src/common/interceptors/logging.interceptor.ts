import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  Logger,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler<any>): Observable<any> {
    const httpContext = context.switchToHttp();
    const req = httpContext.getRequest();
    const { method, url, body } = req;
    const startTime = Date.now();

    this.logger.log(`[REQUEST] ${method} ${url}`);
    if (body && Object.keys(body).length > 0) {
      this.logger.debug(`[REQUEST_BODY] ${JSON.stringify(body)}`);
    }

    return next.handle().pipe(
      tap((data) => {
        const duration = Date.now() - startTime;
        this.logger.log(`[RESPONSE] ${method} ${url} - ${duration}ms`);
        if (data) {
          this.logger.debug(`[RESPONSE_DATA] ${JSON.stringify(data).substring(0, 200)}`);
        }
      }),
      catchError((error) => {
        const duration = Date.now() - startTime;
        this.logger.error(`[ERROR] ${method} ${url} - ${error.message} (${duration}ms)`);
        throw error;
      }),
    );
  }
}
