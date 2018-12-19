import { Component, OnInit } from '@angular/core';
import { LoggerService } from '../util/logger.service';
import { BackendService, BackendVersion } from '../backend/backend.service';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  showAboutModal: boolean = false;
  versionString: string = "";

  constructor(private log: LoggerService, private backend: BackendService) { }

  ngOnInit() {
  }

  getVersionFromBackend() {
    this.backend.getBackendVersion().subscribe(
      data => {
        let version: BackendVersion = data;
        this.log.info("Version from backend: %s", version.version);
        this.versionString = version.version;
      },
      error => {
        this.log.error("Failed to get app version from the backend");
        // This is not a fatal error, so skip showing any error dialog
      }
    );
  }

  updateVisibilityState(newState: boolean) {
    this.showAboutModal = newState;
  }

  showAboutDialog() {
    // Call a REST API to get the version string, then show the dialog
    this.getVersionFromBackend();
    this.showAboutModal = true;
  }

}
