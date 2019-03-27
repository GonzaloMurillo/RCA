import { Component, OnInit } from '@angular/core';
import { LoggerService } from 'src/app/util/logger.service';

@Component({
  selector: 'app-error-dialog',
  templateUrl: './error-dialog.component.html',
  styleUrls: ['./error-dialog.component.css']
})
export class ErrorDialogComponent implements OnInit {

  showErrorModal: boolean = false;
  errorMessage: string = "";

  constructor(private log: LoggerService) { }

  updateVisibilityState(newState: boolean) {
    this.showErrorModal = newState;
  }

  /**
   * Call this public API from the parent component to display a modal error dialog.
   * HTML tags in the message are rendered as-is.
   * 
   * @param message String to be displayed on the modal dialog
   */
  showError(message: string) {
    this.log.error(message);
    this.errorMessage = message;
    this.showErrorModal = true;
  }

  ngOnInit() {
  }

}
