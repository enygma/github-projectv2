# ProjectV2 Client

This is an in-progress client to use the ProjectV2 functionality through the GitHub GraphQL API.

## Setup

1. Install the `projectv2` module: `pip3 install github-projectv2`
2. Create a `.env` file in the root containing a value for `GITHUB_API_TOKEN` (this will be loaded using `python-dotenv`)
3. Use the `requirements.txt` file to ensure you have all of the dependencies you need.
4. Enjoy!

**NOTE:** You can use an actual environment variable instead of the `.env` approach, setting the same `GITHUB_API_TOKEN` value

## Example Usage

```python
from projectv2.project import Project

project = Project()
project.get('myorg', '1234')
print(project.title)

# Find the field with the name "Test Field 1"
found = None
for field in project.fields:
    if field.name == "Test Field 1":
        found = field

if found is None:
    raise Exception("Field not found")

items = project.get_items('myorg')
print(items)

# Look on the project fields and find the one with the name "Test Field 1" and get its options
# Then, find the option with the name "Option 1" and get its id

for option in found.options:
    if option.name == "test3":
        newOption = option

for item in items:
    result = item.update_field_value(project, field, newOption)
    print(result)
```

## Modules

### Project
The `Project` module is used to get the information about a project. It results in an instance with the following properties:

- `title` (string)
- `description` (string)
- `id` (string): internal ID of project record
- `number` (integer): public-facing ID number of project
- `fields` (list): Set of fields in the project, default and custom
- `items` (list): Set of "items" in the project, usually issue instances
- `org` (string): Name of the organization the project belongs to
- `createdAt` (datetime): Date/time of project creation
- `closedAt` (datetime): Date/time when project was closed
- `closed` (boolean): The open/closed state of the project
- `shortDescription` (string): Short description of the project
- `public` (boolean): Visibility for the project (public=`True`, private=`False`)
- `readme` (string): Full readme for the project
- `url` (string): Full public-facing URL location of the project

**NOTE:** When the `get` method is called on the `Project`, the `get_fields` method will automatically be called to populate the `fields` property with instances of the `Field` class.

#### Methods

`get(org, projectNumber)`: Get a project by organization name and public-facing project number
Where:
- `org` (string): the name of the organization
- `projectNumber` (string): the public-facing ID for the project

`get_fields(org)`: Get the fields for a project given the organization name and public-facing project number
Where:
- `org` is the name of the organization (optional)

`get_field(name)`: Get a single field from a project
Where:
- `name` is the name of the field (title)

`get_items(args)`: Get the items currently in the project (issues)
Where `args` are one or more named variables:
- `org` (string) is the name of the organization
- `options` (dict) are options for the query (see "Query Options" section below)
Returns:
- A set of `Item` object types

`get_views(args)`: Get the current list of views for the project
Where `args` are one or more named variables:
- `org` (string): optional name of the organization
- `options` (dict) are options for the query (see "Query Options" section below)
Returns:
- A set of `View` object types

`create(data)`: Create a new project
Where:
- `data` (list): Data to use in the creation of the project (required values: `title`, `ownerId`)
Returns:
- A `Project` instance with the new data set

`remove_item(item)`: Removes an item from a project
Where:
- `item` must be a record as fetched by `get_items`, not from a call to `Item.get`
Returns:
- The internal ID of the deleted item

`add_item(item)`: Adds an item/issue to a project
Where:
- `item` is a record as fetched by `Item.get` or from the list from `Project.get_items`
Returns:
- The internal ID of the item that was added

`save()`: Saves the current state of the project record (fields saved are title, shortDescription, readme, closed)
Returns:
- The current instance, a `Project` with the updated information

**NOTE:** the `get_fields` and `get_items` require that the project is fetched using `get` first and will throw an error otherwise.

### Item
The `Item` module is used to represent an item in a project (an issue or draft issue record). It results in an instance with the following properties:

- `id` (string): internal ID of the item record
- `type` (string): type of item (ex: `ISSUE`)
- `created` (string): A date/time of when the item was created
- `assignees` (list): A set of `User` instances
- `title` (string): Title of the item (issue)
- `number` (string): The public-facing number of the item
- `updatedAt` (string): A date/time of when the item was last updated
- `url` (string): The public-facing URL
- `body` (string): Unrendered body content
- `closed` (boolean): Closed/not closed state
- `closedAt` (string): A date/time of when the issue was closed
- `author` (list): A set of `User` instances
- `labels` (list): A set of `Label` instances
- `projectNodeId` (string): The internal ID of the item (used when relating to a project, otherwise `None`)
- `trackedIssues` (list): A set of `Item` instances
- `trackedInIssues` (list): A set of `Item` instances
- `timeline` (list): A set of `*Event` instances (see below for which events are currently supported)

#### Methods

`update_field_value(project, field, input)`: Update a single select field to a new value
Where:
- `project` = a `Project` instance
- `field` = a `Field` instance representing the field to update the value on
- `option` = Either an an `Option` instance representing the new value or a string value

`get(org, repo, itemId)`
Where:
- `org` (string): the name of the organization
- `repo` (string): the name of the repository
- `itemId` (string): the ID number of the item

`clear_field_value(project, field)`
Where:
- `project`: a `Project` instance
- `field`: a `Field` instance for the field to clear (a result of the objects loaded from a `Project.get_fields()` method call)

`create(repository, data)`
Where:
- `repository`: a `Repository` instance
- `data`: a data set containing the details of the issue you want to create (see below for more detail)

The following are possible values for the `data` to contain:

- `body` (string, required): the body contents for the issue
- `title` (string, required): the title of the issue
- `assigneeIds` (list, optional): a set of IDs relating to the users you want to assign
- `assignees` (list, optional): a set of usernames for the users you want to assign
- `labelIds` (list, optional): a set of IDs related to the labels you want to apply to the issue
- `labels`(list, optional): a set of label names to apply to the issue
- `milestoneId` (string, optional): an ID related to the milestone to link to the issues

> Note: if `assigneeIds` is set, it will override `assignees`. Likewise, if `labelIds` is set, it will override the `labels` value

`add_label(label_name)`
Where:
- `label_name` is the "name" of the label to add (not the ID)

`close(reason)`
Where:
- `reason` (string, optional) either `COMPLETED` or `NOT_PLANNED` (default is `COMPLETED`)

`make_comment(comment)`
Where:
- `comment` (string) is the contents of the comment

`find_field_by_name(name)`
Where:
- `name` (string) is the name of the field to find, works when pulled via projects and `get_items` (`None` if field not found)

`add_subissue(item)`
Where:
- `issue` (Item) is an Item instance of the issue you want to add to the current one as a sub-issue

### Option
The `Option` module is used to represent an option on a single-select field. It results in an instance with the following properties:

- `id` (string): internal ID of the option record
- `name` (string): the name of the option (this is the option's value)

### Field
The `Field` module is used to represent a field in the project. It results in an instance with the following properties:

- `id` (string): internal ID of the field record
- `name` (string): name of the field
- `dataType` (string): type of field (Ex: `TEXT` or `SINGLE_SELECT`)
- `options` (list): when the `dataType` is `SINGLE_SELECT` the options array will be populated with the options records as instances of `Option`

#### Methods

`find_option(name)`
Where:
- `name` is the name (value) of the option. NOTE: only works with single select fields and will throw an error otherwise

### Label
The `Label` module is used to represent a label on an item. It results in an instance with the following properties:

- `id` (string): internal ID of the label record
- `name` (string): name of the label
- `description` (string): description of the label

### User
The `User` module is used to represent a user in the system. It results in an instance with the following properties:

- `id` (string): internal ID of the user record
- `email` (string): email address of the user
- `login` (string): login/username of the user
- `name` (string): user's name

### Milestone
The `Milestone` module is used to represent a milestone in the system. It results in an instance with the following properties:

- `id` (string): internal ID of the milestone record
- `description` (string): description of the milestone
- `number` (integer): public-facing ID
- `title` (string): title of the milestone
- `state` (string): open/closed status
- `dueOn` (string): datetime string of when the milestone is

#### Methods

`get(org)`
Where:
- `org` (string): the name of the organization

### Repository
The `Repository` module is used to represent a repository in the system. It results in an instance with the following properties:

- `id` (string): internal ID of the repository record
- `name` (string): name of the repository
- `description` (string): repository description
- `isPrivate` (boolean): public/private status
- `isArchived` (boolean): archived/not archived
- `isDisabled` (boolean): disabled/not disabled
- `isFork` (boolean): is a fork/not a fork
- `isLocked` (boolean): is locked/not locked
- `isMirror` (boolean): is a mirror/not a mirror
- `isTemplate` (boolean): is a template/not a template

#### Methods

`get(org, name)`
Where:
- `org` (string): organization name
- `name` (string): repository name

`get_milestones()`

**NOTE:** `get_milestones` requires that `get()` is called first

### Comment
The `Comment` module is used to represent a comment instance on an item. It results in an instance with the following properties:

- `id` (string) internal ID of the comment record
- `body` (string) the contents of the comment body
- `updatedAt` (string) the timestamp when the comment was created
- `author` (User) a User object instance for the author of the comment

#### Methods
`delete()`
Where:
    It will delete the comment represented by the current instance

### Organization
The `Organization` module is used to represent an organization in the system. It results in an instance with the following properties:

- `id` (string): internal ID of the organization record
- `name` (string): name of the organization (ex: `GitHub`)
- `login` (string): the login of the organization (ex: `github`)
- `description` (string): the description of the organization
- `createdAt` (string): datetime string
- `location` (string): location value of the organization
- `url` (string): external URL location
- `repositories` (list): a list of all repositories in the organization (loads as `Repository objects`)

**NOTE:** Repositories are not loaded by default. `get_repositories` must be called to load them. The method will also return the repository list.

#### Methods
`get(login)`
Where:
- `login` (string) the name of the organization
Returns:
- A single object of type `Organization`

`get_repositories(login)`
Where:
- `login` (string): the name of the organization (`name` is optional, but if not set `get` must be called first)
Returns:
- A set of `Repository` class objects populated with repository data

### Search
The `Search` module is used to make searches using the `search()` method on the GraphQL API using a format similar to those used in the search on the website.

- No properties defined

#### Methods
`issues`
Where:
- `filter` (string): the search filter string, passed using nameed parameter `filter=...`
- `slim` (string): tell the search method to pull a "slim" version of the issues
Returns:
- Set of `Item` class objects populated with matching issue data

### View
The `View` module represents a view in the project (a tab). It results in an instance with the following properties:

- `id` (string): internal ID of the view
- `number` (string): the public ID of the view
- `sortBy` (array): populated when a view is sorted (contains: `field.name`, `field.id` (internal), `field.dataType`, `direction`)
- `groupBy` (array): populated when a view is grouped (contains: `id` (internal), `name`)
- `layout` (string): Layout of the view (ex: `TABLE_LAYOUT` or `BOARD_LAYOUT`)

Resource: [https://mathspp.com/blog/how-to-create-a-python-package-in-2022](https://mathspp.com/blog/how-to-create-a-python-package-in-2022)

### Timeline Events
Several of the methods, including `item.get` and `project.get_items` (if the value for `includeTimelineEvents` is `True`) will also pull in the timeline events for an item. This timeline provides details about actions like: when an issue was labeled, when someone subscribed to an issue, and when a user was mentioned in an issue. We currently support several event types:

- `AddedToProjectEvent`
- `AssignedEvent`
- `ClosedEvent`
- `CommentDeletedEvent`
- `CrossReferencedEvent`
- `IssueComment`
- `IssueTypeAddedEvent`
- `IssueTypeChangedEvent`
- `LabeledEvent`
- `MentionedEvent`
- `MovedColumnsInProjectEvent`
- `ParentIssueAddedEvent`
- `ParentIssueRemovedEvent`
- `PinnedEvent`
- `ReferencedEvent`
- `RenamedTitleEvent`
- `ReopenedEvent`
- `SubIssueAddedEvent`
- `SubIssueRemovedEvent`
- `SubscribedEvent`
- `UnassignedEvent`
- `UnlabeledEvent`
- `UnsubscribedEvent`

You can find out more about what properties each of these support [in the GitHub API object documentation](https://docs.github.com/en/graphql/reference/objects).

## Query Options
In some methods (such as `project.get_items`) use can used named arguments to configure the requests made to the API (see method definitions above to determine which support the `options` named variable)

### Supported options:
- `includeTrackedInIssues`: Includes information about the other item(s) the current item is tracked in (Values: `True`/`False`)
- `includeTrackedIssues`: Include information about the item(s) being tracked by this item  (Values: `True`/`False`)
- `includeTimelineEvents`: Include the timeline events that were taken on the item (Values: `True`/`False`)
- `includeFields`: Include the field information in the item, works when pulled via a project (Values: `True`/`False`)
- `useSlimIssue`: Return the items with the "slim" version of the results (Values: `True`/`False`)

### Development

This package makes use of the [Poetry](https://python-poetry.org/) packaging tool. In order to do development work, you should perform the following steps:

```
cd projectv2
poetry shell
```

Then you can run your script from there. In my case, it's one called `test.py` that lives one directory up, so: `python3 ../test.py`

Then, to package, build, and push it up to the PyPi platform:

1. Update the `version` in `pyproject.toml`
2. Commit the changes and add a new tag
3. Push the updates to the repo (including the new tag)
4. Run the build and push commands from outside of the `poetry` shell:

```
poetry build
poetry publish
```
