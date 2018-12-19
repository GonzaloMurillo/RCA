import { Injectable } from '@angular/core';
import { HttpErrorResponse, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { ErrorObservable } from 'rxjs/observable/ErrorObservable';
import { catchError, retry } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { LoggerService } from '../util/logger.service';

export interface BackendVersion {
  version: string;
}

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  
  urls = {
    version: 'api/version'
  }

  constructor(private log: LoggerService, private http: HttpClient) { }

  /**
   * Common handler for all REST API call failures
   * 
   * @param error HTTP error from REST API response
   */
  private handleApiResponseError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred.
      this.log.error("Client-side failure for REST API call: " + error.error.message);
    } else {
      // The server returned an error HTTP status code
      this.log.error("REST API failed, response: " + error);
    }

    return new ErrorObservable();
  }

  private handleError(operation = 'operation') {
    return (error: any) => {
      let errorMessage = error.message;
      
      if (error instanceof HttpErrorResponse) {
        // Sample: {operation} failed with HTTP 400 (BAD REQUEST): {custom error msg string from server} 
        this.log.error(`${operation} failed with HTTP ${error.status} (${error.statusText}): `, error.error);
        errorMessage = error.error;
      } else {
        this.log.error(`${operation} failed: `, error.message);
      }

      return throwError(errorMessage);
    };
  }

  getBackendVersion(): Observable<BackendVersion> {
    return this.http.get<BackendVersion>(this.urls.version)
      .pipe(
        catchError(this.handleError('getVersion'))
      );
  }
}
