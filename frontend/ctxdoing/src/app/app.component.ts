import { Component } from '@angular/core';
import { LoggerService } from './util/logger.service';
import { BackendService } from './backend/backend.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'ctxdoing';

  constructor(private log: LoggerService, private backend: BackendService, private router: Router) {}

  onLogout() {
    this.log.info("Logging out as user: ", this.backend.logged_in_user);

    this.backend.doLogout().subscribe(
      data => {
        this.router.navigate(['login'])
      },
      error => {
        this.log.error("Failed to logout");

        // Don't bother showing an error, just navigate to the login page again
        this.router.navigate(['login']);
      }
    )
  }
}
