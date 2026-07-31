#!/usr/bin/env python3
"""
SmartShop AI - Command Line Interface
Provides easy access to the pipeline, server, and utilities.
"""
import click
import sys
import os
import importlib
import uvicorn
from graph.pipeline import run_price_pipeline


@click.group()
def cli():
    """SmartShop AI - Price Intelligence System CLI"""
    pass


@cli.command()
@click.option('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
@click.option('--port', default=8000, type=int, help='Server port (default: 8000)')
@click.option('--reload', is_flag=True, help='Enable auto-reload on file changes')
def server(host, port, reload):
    """Start the FastAPI backend server"""
    click.echo(f"🚀 Starting SmartShop AI server at http://{host}:{port}")
    click.echo("   API docs: http://localhost:8000/docs")
    click.echo("   Health check: http://localhost:8000/api/health")
    click.echo("")
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        click.echo("\n✅ Server stopped")
        sys.exit(0)


@cli.command()
@click.argument('product_name')
@click.option('--email', default='test@example.com', help='User email for tracking (default: test@example.com)')
@click.option('--verbose', is_flag=True, help='Show detailed pipeline output')
def search(product_name, email, verbose):
    """Search for a product and get AI-powered price analysis
    
    Example:
        python cli.py search "iPhone 15"
        python cli.py search "Samsung Galaxy S24" --email user@example.com
    """
    click.echo(f"\n🔍 Searching for: {product_name}")
    click.echo(f"📧 User email: {email}")
    click.echo("⏳ Running pipeline (this may take 1-2 minutes)...\n")
    
    try:
        result = run_price_pipeline(product_name, email)
        
        # Display results
        click.echo("\n" + "="*60)
        click.echo("🤖 AI PREDICTION:")
        click.echo("="*60)
        
        if result.get('ai_prediction'):
            click.echo(result['ai_prediction'])
        else:
            click.echo("❌ No prediction generated")
        
        click.echo("\n" + "="*60)
        click.echo(f"🔔 Alert Status: {result.get('alert_status', 'N/A')}")
        click.echo("="*60 + "\n")
        
        if verbose and result.get('raw_products'):
            click.echo("\n📊 Raw Products Found:")
            for i, prod in enumerate(result.get('raw_products', [])[:5], 1):
                click.echo(f"  {i}. {prod.get('title', 'N/A')} @ {prod.get('price', 'N/A')}")
    
    except Exception as e:
        click.echo(f"\n❌ Pipeline failed: {type(e).__name__}: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo("\nFull traceback:", err=True)
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
def health():
    """Check the health of the project (imports, database, dependencies)"""
    click.echo("\n🔍 SmartShop AI Health Check\n")
    
    checks = {
        "Importing main FastAPI app": lambda: getattr(importlib.import_module('main'), 'app'),
        "Importing pipeline": lambda: importlib.import_module('graph.pipeline'),
        "Importing agents": lambda: importlib.import_module('agents.product_finder'),
        "Supabase connection": lambda: getattr(importlib.import_module('utils.supabase_client'), 'db'),
    }
    
    passed = 0
    failed = 0
    
    for check_name, check_fn in checks.items():
        try:
            check_fn()
            click.echo(f"✅ {check_name}")
            passed += 1
        except Exception as e:
            click.echo(f"❌ {check_name}: {str(e)[:60]}")
            failed += 1
    
    click.echo(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        click.echo("\n✨ All systems operational!\n")
        sys.exit(0)
    else:
        click.echo(f"\n⚠️  {failed} check(s) failed. See messages above.\n")
        sys.exit(1)


@cli.command()
def test():
    """Run the test suite"""
    click.echo("\n🧪 Running SmartShop AI Test Suite\n")
    
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=os.getcwd()
    )
    
    sys.exit(result.returncode)


@cli.command()
def info():
    """Show project information and configuration"""
    click.echo("\n" + "="*60)
    click.echo("SmartShop AI - Project Information")
    click.echo("="*60)
    
    click.echo("\n📦 Project Structure:")
    click.echo("  • Agents: agents/")
    click.echo("  • Pipeline: graph/pipeline.py")
    click.echo("  • Backend: main.py (FastAPI)")
    click.echo("  • Frontend: SmartShopAI/ (React Native)")
    click.echo("  • Tests: tests/")
    click.echo("  • Utils: utils/")
    
    click.echo("\n🔧 Key Technologies:")
    click.echo("  • FastAPI (Backend)")
    click.echo("  • LangGraph (Agent orchestration)")
    click.echo("  • Cohere (LLM)")
    click.echo("  • Supabase (Database)")
    click.echo("  • React Native (Frontend)")
    
    click.echo("\n📚 Quick Links:")
    click.echo("  • Docs: http://localhost:8000/docs")
    click.echo("  • API health: http://localhost:8000/api/health")
    click.echo("  • README: README.md")
    click.echo("  • Quick start: QUICKSTART.md")
    
    click.echo("\n💡 Common Commands:")
    click.echo("  python cli.py server              # Start the backend server")
    click.echo("  python cli.py search iPhone15     # Search for a product")
    click.echo("  python cli.py health              # Check system health")
    click.echo("  python cli.py test                # Run test suite")
    click.echo("")


if __name__ == '__main__':
    cli()
