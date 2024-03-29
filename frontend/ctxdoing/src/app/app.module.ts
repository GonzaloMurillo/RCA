import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';


import { ClarityModule } from '@clr/angular';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgxChartsModule } from '@swimlane/ngx-charts';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AboutComponent } from './about/about.component';
import { ConsoleLoggerService } from './util/console-logger.service';
import { LoggerService } from './util/logger.service';
import { HttpClientModule } from '@angular/common/http';
import { AsupInputComponent } from './main-wizard/asup-input/asup-input.component';
import { ReplicationCtxSelectionComponent } from './main-wizard/replication-ctx-selection/replication-ctx-selection.component';
import { ReplicationAnalysisComponent } from './main-wizard/replication-analysis/replication-analysis.component';
import { FormsModule } from '@angular/forms';
import { ErrorDialogComponent } from './error-dialog/error-dialog.component';
import { SelectAsupComponent } from './main-wizard/asup-input/select-asup/select-asup.component';
import { LoginComponent } from './login/login.component';

@NgModule({
  declarations: [
    AppComponent,
    AboutComponent,
    AsupInputComponent,
    ReplicationCtxSelectionComponent,
    ReplicationAnalysisComponent,
    ErrorDialogComponent,
    SelectAsupComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ClarityModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    NgxChartsModule
  ],
  providers: [
    { provide: LoggerService, useClass: ConsoleLoggerService }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
