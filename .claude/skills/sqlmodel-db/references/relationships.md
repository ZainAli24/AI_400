# Model Relationships

Guide to implementing One-to-Many and Many-to-Many relationships in SQLModel.

## One-to-Many Relationship

The most common relationship: one record links to many records.

**Example**: One Team has many Users

```python
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # One team has many members
    members: list["User"] = Relationship(back_populates="team")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Foreign key to team
    team_id: int | None = Field(default=None, foreign_key="team.id")

    # Relationship back to team
    team: Team | None = Relationship(back_populates="members")
```

### Understanding the Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `foreign_key="team.id"` | User (child) | Links to Team's primary key |
| `Relationship(back_populates="team")` | Team (parent) | Access users via `team.members` |
| `Relationship(back_populates="members")` | User (child) | Access team via `user.team` |

### Creating Related Records

```python
from sqlmodel import Session

# Method 1: Create team first, then add users
team = Team(name="Engineering")
session.add(team)
session.commit()
session.refresh(team)

user = User(name="Alice", team_id=team.id)
session.add(user)
session.commit()

# Method 2: Create with relationship
team = Team(name="Engineering")
user = User(name="Alice", team=team)  # Assign team object directly

session.add(team)
session.add(user)
session.commit()
```

### Querying Related Data

```python
# Get team with all members
team = session.get(Team, 1)
print(team.name)           # "Engineering"
print(team.members)        # [User(id=1, name="Alice"), ...]

# Get user with their team
user = session.get(User, 1)
print(user.name)           # "Alice"
print(user.team.name)      # "Engineering"
```

### API Endpoints with Relationships

```python
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

# Create user in a team
@app.post("/teams/{team_id}/users", response_model=User)
def add_user_to_team(
    team_id: int,
    user: UserCreate,
    session: Session = Depends(get_session)
):
    # Verify team exists
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db_user = User(**user.model_dump(), team_id=team_id)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Get all users in a team
@app.get("/teams/{team_id}/users", response_model=list[User])
def get_team_users(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.members
```

## One-to-Many: Complete Example

**Scenario**: Users can create multiple Tasks

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# --- User Models ---
class UserBase(SQLModel):
    username: str
    email: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One user has many tasks
    tasks: list["Task"] = Relationship(back_populates="owner")

class UserCreate(UserBase):
    pass

class UserPublic(UserBase):
    id: int

# --- Task Models ---
class TaskBase(SQLModel):
    title: str
    description: str | None = None

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to user
    owner_id: int = Field(foreign_key="user.id")

    # Relationship back to user
    owner: User = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskPublic(TaskBase):
    id: int
    completed: bool
    owner_id: int
```

## Many-to-Many Relationship

When records on both sides can have multiple connections.

**Example**: Users can belong to multiple Projects, Projects can have multiple Users

### Step 1: Create Link Table

```python
from sqlmodel import SQLModel, Field

class UserProjectLink(SQLModel, table=True):
    """Link table for many-to-many relationship"""
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)
```

### Step 2: Define Models with Relationships

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Many-to-many: user can be in multiple projects
    projects: list["Project"] = Relationship(
        back_populates="members",
        link_model=UserProjectLink
    )

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Many-to-many: project can have multiple members
    members: list[User] = Relationship(
        back_populates="projects",
        link_model=UserProjectLink
    )
```

### Managing Many-to-Many

```python
# Create user and project
user = User(name="Alice")
project = Project(name="Website Redesign")

session.add(user)
session.add(project)
session.commit()
session.refresh(user)
session.refresh(project)

# Add user to project
user.projects.append(project)
session.add(user)
session.commit()

# Or add project to user's list
project.members.append(user)
session.add(project)
session.commit()
```

### API Endpoints for Many-to-Many

```python
# Add user to project
@app.post("/projects/{project_id}/members/{user_id}")
def add_member(
    project_id: int,
    user_id: int,
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    user = session.get(User, user_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    if user in project.members:
        raise HTTPException(status_code=400, detail="Already a member")

    project.members.append(user)
    session.add(project)
    session.commit()

    return {"message": f"Added {user.name} to {project.name}"}

# Remove user from project
@app.delete("/projects/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    user = session.get(User, user_id)

    if not project or not user:
        raise HTTPException(status_code=404, detail="Not found")

    if user not in project.members:
        raise HTTPException(status_code=400, detail="Not a member")

    project.members.remove(user)
    session.add(project)
    session.commit()

    return {"message": f"Removed {user.name} from {project.name}"}

# Get project members
@app.get("/projects/{project_id}/members", response_model=list[UserPublic])
def get_members(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.members

# Get user's projects
@app.get("/users/{user_id}/projects", response_model=list[ProjectPublic])
def get_user_projects(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.projects
```

## Many-to-Many with Extra Data

Sometimes the link table needs additional fields:

```python
from datetime import datetime

class UserProjectLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

    # Extra fields on the relationship
    role: str = "member"  # "admin", "member", "viewer"
    joined_at: datetime = Field(default_factory=datetime.utcnow)
```

To access extra fields, query the link table directly:

```python
# Get user's role in a project
link = session.exec(
    select(UserProjectLink).where(
        UserProjectLink.user_id == user_id,
        UserProjectLink.project_id == project_id
    )
).first()

if link:
    print(f"Role: {link.role}, Joined: {link.joined_at}")
```

## Self-Referential Relationships

A model that references itself (e.g., organizational hierarchy):

```python
class Employee(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    # Self-reference: manager is also an Employee
    manager_id: int | None = Field(default=None, foreign_key="employee.id")

    # Relationship to manager (parent)
    manager: "Employee | None" = Relationship(
        back_populates="direct_reports",
        sa_relationship_kwargs={"remote_side": "Employee.id"}
    )

    # Relationship to direct reports (children)
    direct_reports: list["Employee"] = Relationship(back_populates="manager")
```

## Cascade Delete

When deleting a parent, automatically delete children:

```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    members: list["User"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

Now when you delete a team, all its members are also deleted:

```python
team = session.get(Team, 1)
session.delete(team)  # Also deletes all team.members
session.commit()
```

## Lazy vs Eager Loading

### Default (Lazy Loading)
Related objects are loaded only when accessed:

```python
team = session.get(Team, 1)  # Only loads team
print(team.members)           # NOW loads members (extra query)
```

### Eager Loading (selectinload)
Load related objects in the initial query:

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Load team AND members in one query
statement = select(Team).options(selectinload(Team.members)).where(Team.id == 1)
team = session.exec(statement).first()

print(team.members)  # Already loaded, no extra query
```

### When to Use Eager Loading

Use `selectinload` when you know you'll need related data:

```python
@app.get("/teams/{team_id}")
def get_team_with_members(team_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id)
    )
    team = session.exec(statement).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return {
        "id": team.id,
        "name": team.name,
        "member_count": len(team.members),
        "members": [{"id": m.id, "name": m.name} for m in team.members]
    }
```

## Response Models with Relationships

When returning related data, create specific response models:

```python
class UserWithTeam(SQLModel):
    """User response including team info"""
    id: int
    name: str
    team: TeamPublic | None

class TeamWithMembers(SQLModel):
    """Team response including all members"""
    id: int
    name: str
    members: list[UserPublic]

@app.get("/users/{user_id}", response_model=UserWithTeam)
def get_user_with_team(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Complete Example: Blog with Authors and Tags

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

# --- Link Table for Posts <-> Tags (Many-to-Many) ---
class PostTagLink(SQLModel, table=True):
    post_id: int = Field(foreign_key="post.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

# --- Author (One-to-Many with Posts) ---
class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    posts: list["Post"] = Relationship(back_populates="author")

# --- Tag (Many-to-Many with Posts) ---
class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    posts: list["Post"] = Relationship(
        back_populates="tags",
        link_model=PostTagLink
    )

# --- Post (Many-to-One with Author, Many-to-Many with Tags) ---
class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to author
    author_id: int = Field(foreign_key="author.id")

    # Relationships
    author: Author = Relationship(back_populates="posts")
    tags: list[Tag] = Relationship(
        back_populates="posts",
        link_model=PostTagLink
    )
```

## Next Steps

- **[best-practices.md](best-practices.md)** - Production patterns and tips
