import click
from utils.database_migration.migration_task import HtmlTaskTag, SubtaskAnnotation


@click.command()
def migrate_db(task_name, *args, **kwargs):
    """Applies Database Migration Tasks.
    The tasks are chosen by a proved string via the command line

    Args:
        task_name ([type]): [description]
    """
    task_mapping = {
        "task_html_entry": HtmlTaskTag,
        "subtask_annotation": SubtaskAnnotation
    }

    migration_task = task_mapping.get(task_name, None)
    if migration_task:
        click.echo(f"Running {migration_task.__name__}...")
        migration_task.run_migration(*args, **kwargs)


if __name__ == "__main__":
    migrate_db()
