import { Component, OnInit, ViewChild } from '@angular/core';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';
import { Router } from '@angular/router';
import { BackendService, AsupFileMetadata } from 'src/app/backend/backend.service';
import { LoggerService } from 'src/app/util/logger.service';

@Component({
  selector: 'app-select-asup',
  templateUrl: './select-asup.component.html',
  styleUrls: ['./select-asup.component.css']
})
export class SelectAsupComponent implements OnInit {

  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;
  
  selectedRows: any[] = [];
  asupFiles: AsupFileMetadata[];

  constructor(private router: Router, private backend: BackendService, private log: LoggerService) { }

  ngOnInit() {
    this.populateAsupFilesList();
  }

  populateAsupFilesList() {

    this.backend.getAsupFilesList().subscribe(
      data => {
        this.log.info("Retrieved ASUP files list from backend: ", data);
        this.asupFiles = data;
      },
      error => {
        this.errorDialog.showError("Failed to read ASUP file(s): " + error);
      }
    );
  }

  /**
   * Validate selection of ASUP files and navigate to the next page
   */
  selectAsupFilesAndProceed() {
    if (0 == this.selectedRows.length) {
      this.errorDialog.showError("Select at least one ASUP file to be analyzed");
      return;
    }

    if (this.selectedRows.length > 2) {
      this.errorDialog.showError("Select either one or at the most two ASUP file(s) to be analyzed");
      return;
    }

    this.backend.setSelectedAsupFilesList(this.selectedRows).subscribe(
      data => {
        this.log.info("Posted selected ASUP files list to backend")
        // Navigate to the next page
        this.router.navigate(['replication-ctx-selection']);
      },
      error => {
        this.errorDialog.showError("Failed to select ASUP files for analysis: " + error);
      }
    );
    
  }

}
