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

export interface AsupFileAutoCoresLocation {
  auto_cores_path: string;
}

export interface AsupFileElysiumSerialNumber {
  elysium_serial_number: string;
}

export interface ReplicationContext {
  ctx: number,
  mtree: string,
  destination: string
}

export interface ReplicationContextAnalysisResult {
  ctx: number,
  mtree: string,
  destination: string,
  graphImage: string,
  ctxUsageTime: any[]
}

@Injectable({
  providedIn: 'root'
})
export class BackendService {

  urls = {
    version: 'api/version',           // GET
    
    asupFileUpload: 'api/asup/file',  // POST with FormData
    asupFileAutoCoresLocation: 'api/asup/auto_cores_path',  // POST with AsupFileAutoCoresLocation
    asupFileElysiumSerialNumber: 'api/asup/elysium_serial_number',  // POST with AsupFileElysiumSerialNumber

    replicationContextsList: '/api/asup/analysis/replication_contexts', // GET, POST with ReplicationContext[]
    replicationContextAnalysisResult: '/api/asup/analysis/replication_contexts/time_spent', // GET with ReplicationContextAnalysisResult[]
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

  postAsupFile(file: File): Observable<any> {
    let formData: FormData = new FormData();
    formData.append('asup', file, file.name);
    return this.http.post(this.urls.asupFileUpload, formData)
      .pipe(
        catchError(this.handleError('postAsupFile'))
      );
  }

  postAsupAutoCoresPath(path: string): Observable<any> {
    let payload: AsupFileAutoCoresLocation = {
      auto_cores_path: path
    };
    return this.http.post(this.urls.asupFileAutoCoresLocation, payload)
      .pipe(
        catchError(this.handleError('postAsupAutoCoresPath'))
      );
  }

  postAsupElysiumSerialNumber(serialNumber: string): Observable<any> {
    let payload: AsupFileElysiumSerialNumber = {
      elysium_serial_number: serialNumber
    };
    return this.http.post(this.urls.asupFileElysiumSerialNumber, payload)
      .pipe(
        catchError(this.handleError('postAsupElysiumSerialNumber'))
      );
  }

  getReplicationContextsList(): Observable<ReplicationContext[]> {
    return this.http.get<ReplicationContext[]>(this.urls.replicationContextsList)
      .pipe(
        catchError(this.handleError('getReplicationContextsList'))
      );
  }

  setSelectedReplicationContextsList(list: ReplicationContext[]) {
    return this.http.post<ReplicationContext[]>(this.urls.replicationContextsList, list)
      .pipe(
        catchError(this.handleError('setSelectedReplicationContextsList'))
      );
  }

  getReplicationContextsAnalysisResult(): Observable<ReplicationContextAnalysisResult[]> {
    return this.http.get<ReplicationContextAnalysisResult[]>(this.urls.replicationContextAnalysisResult)
      .pipe(
        catchError(this.handleError('getReplicationContextsAnalysisResult'))
      );
  }
}
