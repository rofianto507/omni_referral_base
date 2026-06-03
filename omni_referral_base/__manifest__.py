{
    'name': 'Omni Referral Base',
    'version': '19.0.2.0.0',
    'summary': 'Multi-Level Referral Network & Sales Commission for Odoo 19',
    'description': """
        Omni Referral Base is a complete multi-level referral network and 
        commission management module for Odoo 19. 

        Key Features:
        - Multi-level commission rules by depth level
        - Referral member management with network tree visualization
        - Automated commission calculation on Sales Order confirmation
        - Commission cancellation on Sales Order cancellation
        - Commission withdrawal management with approval workflow
        - Interactive dashboard with charts (Apache ECharts)
        - Member card report (printable)
        - Settings integration
            """,
    'category': 'Sales/Sales',
    'author': 'Sel Studio',
    'website': 'https://selstudio.id',
    'maintainer': 'Sel Studio',
    'support': 'support@selstudio.id', 
    'depends': ['base', 'sale_management', 'mail','account'],
    'license': 'OPL-1', 
    'price': 49.0,
    'currency': 'USD',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/withdraw_wizard_views.xml',
        'views/dashboard_views.xml',
        'views/commission_rule_views.xml',
        'views/member_views.xml',
        'views/commission_views.xml',
        'views/commission_withdraw_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/referral_tree_views.xml',
        'views/menu.xml',
        'reports/member_card_report.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'omni_referral_base/static/lib/echarts.min.js',
            'omni_referral_base/static/src/css/referral_tree.css',
            'omni_referral_base/static/src/css/dashboard.css',
            'omni_referral_base/static/src/xml/referral_tree_widget.xml',
            'omni_referral_base/static/src/xml/dashboard.xml',
            'omni_referral_base/static/src/js/referral_tree_widget.js',
            'omni_referral_base/static/src/js/dashboard.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'icon': 'static/description/icon.png',
    'installable': True,
    'application': True, 
    'auto_install': False,
}