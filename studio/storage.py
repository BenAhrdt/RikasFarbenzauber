from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

class ModuleStaticStorage(ManifestStaticFilesStorage):
    # Version the entire import graph, not only the entry script.
    support_js_module_import_aggregation = True
    max_post_process_passes = 20
