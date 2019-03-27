import { Component, OnInit, ViewChild } from '@angular/core';
import { LoggerService } from '../util/logger.service';
import { LoginCredentials, BackendService } from '../backend/backend.service';
import { ErrorDialogComponent } from '../error-dialog/error-dialog.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;

  loginCredentials: LoginCredentials = {
    email: ''
  };

  constructor(private log: LoggerService, private backend: BackendService, private router: Router) { }

  ngOnInit() {
    if (this.backend.is_logged_in) {
      this.log.info("Already logged in as '%s', moving on...", this.backend.logged_in_user.email)
      this.router.navigate(['asup-input']);
    }
  }

  onLogin() {
    this.log.info("Login as: ", this.loginCredentials);

    this.backend.doLogin(this.loginCredentials).subscribe(
      data => {
        this.router.navigate(['asup-input']);
      },
      error => {
        this.errorDialog.showError("Failed to login as '" + this.loginCredentials.email + "'<br><br>" + error);
      }
    );
  }

}
