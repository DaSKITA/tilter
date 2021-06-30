import click
from scripts.database_migration.migration_task import HtmlTaskTag, SubtaskAnnotation, DeleteUnboundObj


@click.command()
@click.option("-t", "--task_name", default="", help="Supply a migration task name.")
def migrate_db(task_name):
    """Applies Database Migration Tasks.
    The tasks are chosen by a proved string via the command line

    Args:
        task_name ([type]): [description]
    """
    task_mapping = {
        "task_html_entry": HtmlTaskTag,
        "subtask_annotation": SubtaskAnnotation,
        "delete_unbound_obj": DeleteUnboundObj
    }

    migration_task = task_mapping.get(task_name, None)
    if migration_task:
        click.echo(f"Running {migration_task.__name__} Migration Task...")
        migration_task.run_migration()
    else:
        click.echo("No migration Task Found")


if __name__ == "__main__":
    migrate_db()
