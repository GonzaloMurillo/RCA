import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  showAboutModal: boolean = false;
  versionString: string = "v1.0.0 beta";

  constructor() { }

  ngOnInit() {
  }

  updateVisibilityState(newState: boolean) {
    this.showAboutModal = newState;
  }

  showAboutDialog() {
    this.showAboutModal = true;
  }

}
