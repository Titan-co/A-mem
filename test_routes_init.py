import traceback

def test_routes_initialization():
    try:
        print("Attempting to import routes module...")
        import routes
        print("Routes module imported successfully!")
        
        # Check if router exists
        if hasattr(routes, 'router'):
            print("Router found in routes module")
        else:
            print("No router found in routes module!")
            
        # Check if memory_system was initialized
        if hasattr(routes, 'memory_system'):
            print("Memory system found in routes module")
        else:
            print("No memory system found in routes module!")
        
        return True
    except Exception as e:
        print(f"Error importing routes module: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Routes Module Initialization")
    print("=" * 50)
    result = test_routes_initialization()
    print("\nTest result:", "SUCCESS" if result else "FAILED")
