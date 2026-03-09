// Runtime verification script - paste this into browser console
console.log('🧪 STARTING RUNTIME VERIFICATION');

// Test 1: Check if services exist
const services = ['stateManager', 'uiService', 'apiService', 'authService', 'webSocketService'];
console.log('📋 Service Check:');
services.forEach(service => {
    const exists = typeof window[service] !== 'undefined';
    console.log(`${service}: ${exists ? '✅ EXISTS' : '❌ MISSING'}`);
});

// Test 2: Check if AppController exists
console.log('📋 AppController Check:');
if (typeof window.appController !== 'undefined') {
    console.log('✅ AppController exists');
    
    // Test 3: Check if it's properly initialized
    if (window.appController.isInitialized) {
        console.log('✅ AppController initialized');
    } else {
        console.log('❌ AppController not initialized');
    }
} else {
    console.log('❌ AppController missing');
}

// Test 4: Check auth modal methods
console.log('📋 Auth Modal Methods Check:');
if (window.uiService) {
    console.log('showAuthModal:', typeof window.uiService.showAuthModal);
    console.log('hideAuthModal:', typeof window.uiService.hideAuthModal);
} else {
    console.log('❌ uiService missing');
}

// Test 5: Manual auth modal test
console.log('📋 Manual Auth Modal Test:');
try {
    if (window.appController && window.appController.showAuthModal) {
        window.appController.showAuthModal();
        console.log('✅ Auth modal should be visible now');
    } else {
        console.log('❌ Cannot show auth modal');
    }
} catch (error) {
    console.log('❌ Auth modal test failed:', error.message);
}

console.log('🧪 RUNTIME VERIFICATION COMPLETE');
