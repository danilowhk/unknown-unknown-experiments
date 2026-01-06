def fibonacci(n): 	    	 
    if n <= 1: 	 	 	  
        return n  		    
    return fibonacci(n-1) + fibonacci(n-2) 		 	 		
 		   	 
def factorial(n): 		 	  	
    if n == 0: 	 	 	 	
        return 1 		  			
    return n * factorial(n-1) 	  		  
 	   	  
def is_prime(n): 	   	 	
    if n < 2:  	 				
        return False 	  		 	
    for i in range(2, int(n**0.5) + 1): 	   	  
        if n % i == 0: 	 	  	 
            return False  	 				
    return True 	 	 			
 	 	 		 
def main(): 	 	 		 
    print("Fibonacci(10):", fibonacci(10)) 	  		  
    print("Factorial(5):", factorial(5)) 	 	  	 
    print("Is 17 prime?", is_prime(17)) 	 		   
 	   	 	
if __name__ == "__main__":  		    
    main() 	  		 	
 				  	