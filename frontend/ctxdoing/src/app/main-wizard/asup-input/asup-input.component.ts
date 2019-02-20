import { Component, OnInit, ViewChild } from '@angular/core';
import { LoggerService } from 'src/app/util/logger.service';
import { ErrorDialogComponent } from 'src/app/error-dialog/error-dialog.component';
import { ClrForm, ClrInputContainer } from '@clr/angular';
import { Router } from '@angular/router';
import { BackendService } from 'src/app/backend/backend.service';

@Component({
  selector: 'app-asup-input',
  templateUrl: './asup-input.component.html',
  styleUrls: ['./asup-input.component.css']
})
export class AsupInputComponent implements OnInit {

  @ViewChild(ClrForm) clrForm;
  @ViewChild("asupFileUploadContainer") asupFileUploadContainer: ClrInputContainer;
  @ViewChild("asupFileAutoCoresPathContainer") asupFileAutoCoresPathContainer: ClrInputContainer;
  @ViewChild("asupFromElysiumSerialNumberContainer") asupFromElysiumSerialNumberContainer: ClrInputContainer;
  @ViewChild("errorDialog") errorDialog: ErrorDialogComponent;

  asupFileSpecificationMethod: string = 'upload';
  localAsupFileUpload: any;
  filesUploaded: number = 0;
  asupFileAutoCoresPath: string = '';
  asupFromElysiumSerialNumber: string = '';


  constructor(private log: LoggerService, private router: Router, private backend: BackendService) { }

  ngOnInit() {
  }

  /**
   * Set the local variable to the file names. 
   * Does not actually upload the files - this is done later on form submit.
   * 
   * @param files List of file selected for upload
   */
  onUploadAsupFile(files: FileList) {
    this.log.info("Selected local ASUP file(s) for upload: ", files);
    this.localAsupFileUpload = files;
    this.clearAllFieldsInvalidMarker();
  }

  /**
   * Clear the 'error' state on any field - this will remove the red marker on all of them
   */
  clearAllFieldsInvalidMarker() {
    this.asupFileUploadContainer.invalid = false;
    this.asupFileAutoCoresPathContainer.invalid = false;
    // this.asupFromElysiumSerialNumberContainer.invalid = false;
  }

  /**
   * Validate form inputs, submit to backend and navigate to next page if backend call succeeds
   */
  selectAsupAndProceed() {
    this.clrForm.markAsDirty();

    if ('upload' == this.asupFileSpecificationMethod && !this.localAsupFileUpload) {
      this.asupFileUploadContainer.invalid = true;
      return;
    } else if ('autoCores' == this.asupFileSpecificationMethod && '' == this.asupFileAutoCoresPath) {
      this.asupFileAutoCoresPathContainer.invalid = true;
      return;
    } else if ('elysium' == this.asupFileSpecificationMethod && '' == this.asupFromElysiumSerialNumber) {
      this.asupFromElysiumSerialNumberContainer.invalid = true;
      return;
    }

    switch (this.asupFileSpecificationMethod) {
      case 'upload': {
        for (var _i = 0; _i < this.localAsupFileUpload.length; _i++) {
          this.backend.postAsupFile(this.localAsupFileUpload[_i]).subscribe(
            data => {
              // Don't try to access _i here, since we are inside an async callback
              this.log.info("Successfully uploaded ASUP file to backend");
              this.filesUploaded++;

              if (this.filesUploaded == this.localAsupFileUpload.length) {
                // Navigate to the next page
                this.router.navigate(['replication-ctx-selection']);
              }
            },
            error => {
              this.errorDialog.showError("Failed to upload ASUP file(s) : " + error);
            }
          );
        }

        break;
      }
      case 'autoCores': {
        this.backend.postAsupAutoCoresPath(this.asupFileAutoCoresPath).subscribe(
          data => {
            this.log.info("Successfully posted ASUP file location'", this.asupFileAutoCoresPath, "' to backend");
            // Navigate to the next page
            this.router.navigate(['replication-ctx-selection']);
          },
          error => {
            this.errorDialog.showError("Failed to post ASUP file location: " + error);
          }
        );

        break;
      }
      case 'elysium': {
        this.backend.postAsupElysiumSerialNumber(this.asupFromElysiumSerialNumber).subscribe(
          data => {
            this.log.info("Successfully posted Elysium serial number '", this.asupFromElysiumSerialNumber, "' to backend");
            // Navigate to the next page
            this.router.navigate(['replication-ctx-selection']);
          },
          error => {
            this.errorDialog.showError("Failed to post Elysium serial number: " + error);
          }
        );

        break;
      }
      default: { // This should never happen
        this.errorDialog.showError("Internal GUI error");
      }
    }

  }

}
