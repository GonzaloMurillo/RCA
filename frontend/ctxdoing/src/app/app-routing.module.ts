import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AsupInputComponent } from './main-wizard/asup-input/asup-input.component';
import { ReplicationCtxSelectionComponent } from './main-wizard/replication-ctx-selection/replication-ctx-selection.component';
import { ReplicationAnalysisComponent } from './main-wizard/replication-analysis/replication-analysis.component';
import { SelectAsupComponent } from './main-wizard/asup-input/select-asup/select-asup.component';
import { LoginComponent } from './login/login.component';

const routes: Routes = [
  {path: '', redirectTo: 'asup-input', pathMatch: 'full'},
  {path: 'login', component: LoginComponent},
  {path: 'asup-input', component: AsupInputComponent},
  {path: 'asup-select', component: SelectAsupComponent},
  {path: 'replication-ctx-selection', component: ReplicationCtxSelectionComponent},
  {path: 'replication-analysis', component: ReplicationAnalysisComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
