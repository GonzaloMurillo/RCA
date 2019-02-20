import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectAsupComponent } from './select-asup.component';

describe('SelectAsupComponent', () => {
  let component: SelectAsupComponent;
  let fixture: ComponentFixture<SelectAsupComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SelectAsupComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectAsupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
