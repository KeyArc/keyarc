---
name: frontend-web-dev
description: Use when building Angular applications, creating TypeScript components, implementing reactive forms, managing state, working with RxJS observables, or developing modern web UI with TypeScript.
---

# Frontend Web Development Expert

## Overview
Expert guidance for building modern web applications with Angular, TypeScript, RxJS, and modern web APIs. Focused on component architecture, reactive programming, and type-safe development.

## When to Use
- Creating Angular components, services, or modules
- Implementing reactive forms or template-driven forms
- Working with RxJS observables and operators
- Managing application state
- Implementing HTTP clients and API integration
- Creating reusable UI components
- Implementing routing and navigation
- Working with Angular dependency injection

## Core Patterns

### Angular Component Structure
```typescript
// Good: Well-structured component with OnPush
import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-user-card',
  templateUrl: './user-card.component.html',
  styleUrls: ['./user-card.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserCardComponent {
  @Input() user!: User;
  @Output() userSelected = new EventEmitter<User>();

  onSelect(): void {
    this.userSelected.emit(this.user);
  }
}
```

```typescript
// Bad: No change detection strategy, any types
@Component({
  selector: 'user-card',
  template: `<div>{{user.name}}</div>`
})
export class UserCard {
  user: any;  // No type safety!
  selected: any;

  select() {
    this.selected(this.user);  // Not using EventEmitter
  }
}
```

### Service with Dependency Injection
```typescript
// Good: Injectable service with proper typing
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly apiUrl = '/api/users';

  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl).pipe(
      map(users => users.filter(u => u.active)),
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    // Proper error handling
    throw new Error(`API Error: ${error.message}`);
  }
}
```

### Reactive Forms
```typescript
// Good: Type-safe reactive forms with validation
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export class UserFormComponent {
  userForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.userForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      name: ['', [Validators.required, Validators.minLength(2)]],
      age: [null, [Validators.min(0), Validators.max(150)]]
    });
  }

  onSubmit(): void {
    if (this.userForm.valid) {
      const userData: UserCreate = this.userForm.value;
      // Process form data
    }
  }
}
```

## Quick Reference: Angular Best Practices

| Pattern | Recommendation |
|---------|---------------|
| Change Detection | Use OnPush for performance |
| State Management | Services with BehaviorSubject for simple cases |
| HTTP Calls | Always type responses, use HttpClient |
| Forms | Reactive forms for complex validation |
| Component Communication | @Input/@Output for parent-child |
| Observables | Always unsubscribe (async pipe or takeUntil) |
| Type Safety | Strict TypeScript, no `any` types |

## Common Mistakes

**Memory leaks from subscriptions:**
```typescript
// Bad: Subscription leak
export class Component {
  ngOnInit() {
    this.service.getData().subscribe(data => {
      this.data = data;
    });  // Never unsubscribed!
  }
}

// Good: Use async pipe (auto-unsubscribes)
export class Component {
  data$ = this.service.getData();
}
// Template: {{ data$ | async }}

// Good: Manual unsubscribe
export class Component implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.service.getData()
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => this.data = data);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Not using strict typing:**
```typescript
// Bad: Lose type safety
users: any[];
getData(): Observable<any> { }

// Good: Proper types
users: User[];
getData(): Observable<User[]> { }
```

**Mutating state directly:**
```typescript
// Bad: Direct mutation
this.users.push(newUser);

// Good: Immutable update
this.users = [...this.users, newUser];
```

## RxJS Patterns

```typescript
// Good: Combining multiple observables
import { combineLatest, forkJoin } from 'rxjs';
import { switchMap, debounceTime, distinctUntilChanged } from 'rxjs/operators';

// Search with debounce
searchTerm$: Observable<string> = this.searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.service.search(term))
);

// Parallel requests
forkJoin({
  users: this.userService.getUsers(),
  teams: this.teamService.getTeams()
}).subscribe(({ users, teams }) => {
  // Both completed
});

// Reactive combinations
combineLatest([this.filter$, this.users$]).pipe(
  map(([filter, users]) => users.filter(u => u.name.includes(filter)))
);
```

## TypeScript Best Practices

```typescript
// Good: Strict interfaces and types
interface User {
  readonly id: number;
  email: string;
  name: string;
  createdAt: Date;
}

type UserCreate = Omit<User, 'id' | 'createdAt'>;
type UserUpdate = Partial<UserCreate>;

// Good: Union types for state
type LoadingState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: User[] }
  | { status: 'error'; error: string };
```

## Testing Patterns

```typescript
// Good: Component testing with TestBed
import { ComponentFixture, TestBed } from '@angular/core/testing';

describe('UserCardComponent', () => {
  let component: UserCardComponent;
  let fixture: ComponentFixture<UserCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserCardComponent ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserCardComponent);
    component = fixture.componentInstance;
  });

  it('should emit userSelected when clicked', () => {
    const user: User = { id: 1, name: 'Test', email: 'test@example.com' };
    component.user = user;

    let emittedUser: User | undefined;
    component.userSelected.subscribe(u => emittedUser = u);

    component.onSelect();

    expect(emittedUser).toEqual(user);
  });
});
```

## Key Principles

1. **OnPush change detection**: Better performance for components
2. **Reactive programming**: Leverage RxJS observables effectively
3. **Type safety**: Use strict TypeScript, avoid `any`
4. **Immutable updates**: Never mutate state directly
5. **Unsubscribe**: Use async pipe or takeUntil pattern
6. **Dependency injection**: Use services for shared logic
7. **Testing**: Write tests for components and services
