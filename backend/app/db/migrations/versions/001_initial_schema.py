"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-29 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. Sectors
    op.create_table(
        'sectors',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('performance_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('momentum_score', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('market_cap_weight', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_sectors'))
    )
    op.create_index(op.f('ix_sectors_code'), 'sectors', ['code'], unique=True)
    op.create_index(op.f('ix_sectors_name'), 'sectors', ['name'], unique=True)

    # 3. Companies
    op.create_table(
        'companies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('sector_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('cik', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=False, server_default='US'),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], name=op.f('fk_companies_sector_id_sectors'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_companies'))
    )
    op.create_index(op.f('ix_companies_sector_id'), 'companies', ['sector_id'], unique=False)
    op.create_index(op.f('ix_companies_ticker'), 'companies', ['ticker'], unique=True)

    # 4. Stocks
    op.create_table(
        'stocks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('exchange', sa.String(length=50), nullable=False, server_default='NASDAQ'),
        sa.Column('asset_class', sa.String(length=50), nullable=False, server_default='EQUITY'),
        sa.Column('beta', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('pe_ratio', sa.Float(), nullable=True),
        sa.Column('pb_ratio', sa.Float(), nullable=True),
        sa.Column('dividend_yield', sa.Float(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('week_52_high', sa.Float(), nullable=True),
        sa.Column('week_52_low', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('fk_stocks_company_id_companies'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_stocks'))
    )
    op.create_index(op.f('ix_stocks_company_id'), 'stocks', ['company_id'], unique=False)
    op.create_index(op.f('ix_stocks_ticker'), 'stocks', ['ticker'], unique=True)

    # 5. StockOHLCV
    op.create_table(
        'stock_ohlcv',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('stock_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('adjusted_close', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('interval', sa.String(length=10), nullable=False, server_default='1d'),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_stock_ohlcv_stock_id_stocks'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_stock_ohlcv'))
    )
    op.create_index('ix_stock_ohlcv_stock_timestamp', 'stock_ohlcv', ['stock_id', 'timestamp'], unique=False)
    op.create_index('ix_stock_ohlcv_ticker_timestamp', 'stock_ohlcv', ['ticker', 'timestamp'], unique=False)

    # 6. Market Indices
    op.create_table(
        'market_indices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('change', sa.Float(), nullable=False),
        sa.Column('change_pct', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_market_indices'))
    )
    op.create_index(op.f('ix_market_indices_symbol'), 'market_indices', ['symbol'], unique=True)

    # 7. Fundamentals
    op.create_table(
        'fundamentals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('fiscal_quarter', sa.Integer(), nullable=True),
        sa.Column('pe_ratio', sa.Float(), nullable=True),
        sa.Column('forward_pe', sa.Float(), nullable=True),
        sa.Column('pb_ratio', sa.Float(), nullable=True),
        sa.Column('ev_ebitda', sa.Float(), nullable=True),
        sa.Column('fcf_yield_pct', sa.Float(), nullable=True),
        sa.Column('gross_margin_pct', sa.Float(), nullable=True),
        sa.Column('operating_margin_pct', sa.Float(), nullable=True),
        sa.Column('net_margin_pct', sa.Float(), nullable=True),
        sa.Column('roe_pct', sa.Float(), nullable=True),
        sa.Column('roa_pct', sa.Float(), nullable=True),
        sa.Column('current_ratio', sa.Float(), nullable=True),
        sa.Column('debt_to_equity', sa.Float(), nullable=True),
        sa.Column('interest_coverage_ratio', sa.Float(), nullable=True),
        sa.Column('altman_z_score', sa.Float(), nullable=True),
        sa.Column('health_score', sa.String(length=20), nullable=False, server_default='HEALTHY'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('fk_fundamentals_company_id_companies'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_fundamentals'))
    )
    op.create_index('ix_fundamentals_company_year', 'fundamentals', ['company_id', 'fiscal_year'], unique=False)

    # 8. Financial Statements
    op.create_table(
        'financial_statements',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('statement_type', sa.String(length=30), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('fiscal_period', sa.String(length=10), nullable=False, server_default='FY'),
        sa.Column('reported_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('fk_financial_statements_company_id_companies'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_financial_statements'))
    )
    op.create_index('ix_financial_statements_comp_type_year', 'financial_statements', ['company_id', 'statement_type', 'fiscal_year'], unique=False)

    # 9. News
    op.create_table(
        'news',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=True),
        sa.Column('ticker', sa.String(length=10), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sentiment_label', sa.String(length=20), nullable=False, server_default='NEUTRAL'),
        sa.Column('sentiment_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('impact_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('fk_news_company_id_companies'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_news'))
    )
    op.create_index('ix_news_ticker_published', 'news', ['ticker', 'published_at'], unique=False)

    # 10. Anomalies
    op.create_table(
        'anomalies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('stock_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('anomaly_type', sa.String(length=50), nullable=False),
        sa.Column('severity_score', sa.Float(), nullable=False),
        sa.Column('isolation_score', sa.Float(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_anomalies_stock_id_stocks'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_anomalies'))
    )
    op.create_index('ix_anomalies_ticker_timestamp', 'anomalies', ['ticker', 'timestamp'], unique=False)
    op.create_index('ix_anomalies_severity', 'anomalies', ['severity_score'], unique=False)

    # 11. Scenario Reports
    op.create_table(
        'scenario_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('stock_id', sa.String(length=36), nullable=True),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('scenario_type', sa.String(length=50), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_scenario_reports_stock_id_stocks'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_scenario_reports'))
    )
    op.create_index('ix_scenario_reports_ticker_type', 'scenario_reports', ['ticker', 'scenario_type'], unique=False)

    # 12. Portfolios
    op.create_table(
        'portfolios',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, server_default='Primary Portfolio'),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cash_balance', sa.Float(), nullable=False, server_default='100000.0'),
        sa.Column('weighted_beta', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('daily_var_95_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_portfolios_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_portfolios'))
    )
    op.create_index(op.f('ix_portfolios_user_id'), 'portfolios', ['user_id'], unique=False)

    # 13. Positions
    op.create_table(
        'positions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('portfolio_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('shares', sa.Float(), nullable=False),
        sa.Column('avg_cost', sa.Float(), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=False, server_default='Information Technology'),
        sa.Column('beta', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name=op.f('fk_positions_portfolio_id_portfolios'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_positions')),
        sa.UniqueConstraint('portfolio_id', 'ticker', name='uq_position_portfolio_ticker')
    )
    op.create_index(op.f('ix_positions_ticker'), 'positions', ['ticker'], unique=False)

    # 14. Transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('portfolio_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('shares', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name=op.f('fk_transactions_portfolio_id_portfolios'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )
    op.create_index(op.f('ix_transactions_ticker'), 'transactions', ['ticker'], unique=False)
    op.create_index(op.f('ix_transactions_executed_at'), 'transactions', ['executed_at'], unique=False)

    # 15. Watchlists
    op.create_table(
        'watchlists',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_watchlists_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_watchlists')),
        sa.UniqueConstraint('user_id', 'ticker', name='uq_watchlist_user_ticker')
    )
    op.create_index(op.f('ix_watchlists_ticker'), 'watchlists', ['ticker'], unique=False)

    # 16. Chat Sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False, server_default='Market Intelligence Session'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_chat_sessions_user_id_users'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_chat_sessions'))
    )

    # 17. AI Queries
    op.create_table(
        'ai_queries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=50), nullable=False, server_default='MARKET_INTELLIGENCE'),
        sa.Column('ticker_focus', sa.String(length=10), nullable=True),
        sa.Column('thought_steps', sa.JSON(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=False),
        sa.Column('ui_widgets', sa.JSON(), nullable=False),
        sa.Column('guardrail_passed', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], name=op.f('fk_ai_queries_session_id_chat_sessions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_ai_queries_user_id_users'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_queries'))
    )

    # 18. Research Documents
    op.create_table(
        'research_documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=True),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('filing_type', sa.String(length=20), nullable=False, server_default='10-K'),
        sa.Column('fiscal_year', sa.Integer(), nullable=False, server_default='2024'),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('total_chunks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name=op.f('fk_research_documents_company_id_companies'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_research_documents'))
    )
    op.create_index(op.f('ix_research_documents_ticker'), 'research_documents', ['ticker'], unique=False)

    # 19. Research Chunks
    op.create_table(
        'research_chunks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('section', sa.String(length=255), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('vector_id', sa.String(length=100), nullable=True),
        sa.Column('embedding_model', sa.String(length=100), nullable=False, server_default='all-MiniLM-L6-v2'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['research_documents.id'], name=op.f('fk_research_chunks_document_id_research_documents'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_research_chunks'))
    )
    op.create_index('ix_research_chunks_doc_chunk', 'research_chunks', ['document_id', 'chunk_index'], unique=False)

    # Execute TimescaleDB hypertable setup if on PostgreSQL
    try:
        bind = op.get_bind()
        if bind.dialect.name == "postgresql":
            op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            op.execute("SELECT create_hypertable('stock_ohlcv', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);")
    except Exception:
        pass


def downgrade() -> None:
    op.drop_table('research_chunks')
    op.drop_table('research_documents')
    op.drop_table('ai_queries')
    op.drop_table('chat_sessions')
    op.drop_table('watchlists')
    op.drop_table('transactions')
    op.drop_table('positions')
    op.drop_table('portfolios')
    op.drop_table('scenario_reports')
    op.drop_table('anomalies')
    op.drop_table('news')
    op.drop_table('financial_statements')
    op.drop_table('fundamentals')
    op.drop_table('market_indices')
    op.drop_table('stock_ohlcv')
    op.drop_table('stocks')
    op.drop_table('companies')
    op.drop_table('sectors')
    op.drop_table('users')
