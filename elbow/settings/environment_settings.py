from . import PROJECT_ENVIRONMENT


PIPELINE = {
    'PIPELINE_ENABLED': True,
    'PIPELINE_COLLECTOR_ENABLED': True,
    'CSS_COMPRESSOR': 'pipeline.compressors.cssmin.CSSMinCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.slimit.SlimItCompressor',
    'CSSMIN_BINARY': 'cssmin',
    'COMPILERS': ('pipeline.compilers.sass.SASSCompiler',),
    'STYLESHEETS': {
        'base': {
            'source_filenames': (
                'bootstrap-sass/assets/stylesheets/_bootstrap.scss',
                'css/theme.scss',
                'famfamfam-flags/dist/sprite/famfamfam-flags.css',
            ),
            'output_filename': 'dist/base.css',
            'variant': 'datauri',
        },
        'email_css': {
            'source_filenames': (
                'email/email.css',
            ),
            'output_filename': 'email/email.css',
        },
    },
    'JAVASCRIPT': {
        'base': {
            'source_filenames': (
                'jquery/dist/jquery.js',
                'bootstrap-sass/assets/javascripts/bootstrap.js',
                'js/jquery.rss.js',
                'accruejs/jquery.accrue.js', # interst calc
                'moment/moment.js',
                'moment/locale/de.js',
            ),
            'output_filename': 'dist/base.js',
        },
        'project': {
            'source_filenames': (
                'js/docs.js',
            ),
            'output_filename': 'dist/project.js',
        }
    }
}