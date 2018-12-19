import { Injectable } from '@angular/core';
import { Logger } from './logger.service';

// Change this to enable/disable logging globally on the console
export let isLoggingEnabled = true;

const noop = (): any => undefined;

@Injectable({
  providedIn: 'root'
})
export class ConsoleLoggerService implements Logger {

  get info() {
    if (isLoggingEnabled) {
      return console.info.bind(console);
    } else {
      return noop;
    }
  }

  get warn() {
    if (isLoggingEnabled) {
      return console.warn.bind(console);
    } else {
      return noop;
    }
  }

  get error() {
    if (isLoggingEnabled) {
      return console.error.bind(console);
    } else {
      return noop;
    }
  }

  invokeConsoleMethod(type: string, args?: any): void {
    const logFn: Function = (console)[type] || console.log || noop;
    logFn.apply(console, [args]);
  }
}