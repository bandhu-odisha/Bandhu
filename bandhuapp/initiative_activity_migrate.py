"""Data migration helper: program-wide activity categories per initiative app."""

from collections import defaultdict


def migrate_activity_categories_to_program_scope(apps, schema_editor, app_label):
    Activity = apps.get_model(app_label, 'Activity')
    ActivityCategory = apps.get_model(app_label, 'ActivityCategory')

    for activity in Activity.objects.select_related('category').iterator():
        category = activity.category
        if hasattr(category, 'ashram_id') and category.ashram_id and not activity.ashram_id:
            activity.ashram_id = category.ashram_id
            activity.save(update_fields=['ashram_id'])

    by_name = defaultdict(list)
    for category in ActivityCategory.objects.all():
        by_name[category.name].append(category)

    for categories in by_name.values():
        keeper = categories[0]
        for duplicate in categories[1:]:
            Activity.objects.filter(category_id=duplicate.id).update(category_id=keeper.id)
            duplicate.delete()
