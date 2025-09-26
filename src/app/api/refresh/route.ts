import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // First try loading from public directory (most reliable approach for Vercel)
    const publicPath = path.join(process.cwd(), 'public', 'structured_reading_data.json');
    if (fs.existsSync(publicPath)) {
      const publicData = JSON.parse(fs.readFileSync(publicPath, 'utf8'));
      console.log(`📊 Loaded real data from public: books=${publicData.totals?.books}, pages=${publicData.totals?.pages}`);
      return NextResponse.json(publicData);
    }
    
    // Alternative: try data directory (for local development)
    const dataPath = path.join(process.cwd(), 'data', 'structured_reading_data.json');
    if (fs.existsSync(dataPath)) {
      const dataFileContent = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      console.log(`📊 Loaded real data from data/: books=${dataFileContent.totals?.books}, pages=${dataFileContent.totals?.pages}`);
      return NextResponse.json(dataFileContent);
    }
    
    console.error('❌ No structured reading data found');
    return NextResponse.json({ error: 'No reading data found' }, { status: 404 });
  } catch (error) {
    console.error('Error loading structured reading data:', error);
    return NextResponse.json({ error: 'Failed to load reading data' }, { status: 500 });
  }
}
