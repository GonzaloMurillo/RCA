import { Component, OnInit } from '@angular/core';
import { LoggerService } from 'src/app/util/logger.service';
import { ClrLoadingState } from '@clr/angular';
import { timer } from 'rxjs/observable/timer';
import { Router } from '@angular/router';
import { BackendService } from '../backend/backend.service';


@Component({
  selector: 'app-error-dialog',
  templateUrl: './error-dialog.component.html',
  styleUrls: ['./error-dialog.component.css']
})
export class ErrorDialogComponent implements OnInit {

  reportButtonLoading = ClrLoadingState.DEFAULT;
  showErrorModal: boolean = false;
  errorMessage: string = "";
  emailBodyTemplate: string = ""

  constructor(private log: LoggerService, private route: Router, private backend: BackendService) { }

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

    // Prepare the e-mail body template in case the user clicks on 'report issue'
    this.emailBodyTemplate = "What operation were you doing when the error occurred?";
    this.emailBodyTemplate += "\n\nTechnical Details";
    this.emailBodyTemplate += "\n=================";
    this.emailBodyTemplate += "\nUser: " + this.backend.logged_in_user.email;
    this.emailBodyTemplate += "\nLocal time: " + new Date();
    this.emailBodyTemplate += "\nURL: '" + this.route.url + "'";
    this.emailBodyTemplate += "\nError: '" + message + "'";
    this.emailBodyTemplate += "\n\n\nThank you for reporting this issue; you are helping make RCA a better service! We will get back to you shortly.";
    this.emailBodyTemplate = encodeURIComponent(this.emailBodyTemplate);
    this.showErrorModal = true;
  }

  /**
   * The button has an HREF that will open a new email compose window in Outlook - this takes
   * a few seconds to show up, so fake a loading spinner here
   */
  reportIssue() {
    this.reportButtonLoading = ClrLoadingState.LOADING;
    
    const source = timer(5000);
    const subscribe = source.subscribe(val => {
      this.reportButtonLoading = ClrLoadingState.SUCCESS;
    });

  }

  ngOnInit() {
  }

}
