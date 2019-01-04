import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AsupInputComponent } from './main-wizard/asup-input/asup-input.component';
import { ReplicationCtxSelectionComponent } from './main-wizard/replication-ctx-selection/replication-ctx-selection.component';
import { ReplicationAnalysisComponent } from './main-wizard/replication-analysis/replication-analysis.component';

const routes: Routes = [
  {path: '', redirectTo: 'asup-input', pathMatch: 'full'},
  {path: 'asup-input', component: AsupInputComponent},
  {path: 'replication-ctx-selection', component: ReplicationCtxSelectionComponent},
  {path: 'replication-analysis', component: ReplicationAnalysisComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
