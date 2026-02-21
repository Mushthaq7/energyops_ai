import { ExternalLink } from "lucide-react";

interface Citation {
    content: string;
    source: string;
    score: number;
}

const CitationCard = ({ citation }: { citation: Citation }) => {
    return (
        <div className="bg-secondary/40 p-4 rounded-lg border border-white/5 hover:border-primary/30 transition-colors">
            <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-primary uppercase tracking-wider">
                    Source: {citation.source}
                </span>
                <span className="text-xs text-muted-foreground">
                    Score: {citation.score.toFixed(4)}
                </span>
            </div>
            <p className="text-sm text-foreground/80 italic line-clamp-3">
                "{citation.content}"
            </p>
            <div className="mt-2 flex justify-end">
                <button className="text-xs text-primary hover:underline flex items-center gap-1">
                    View Full Document <ExternalLink size={12} />
                </button>
            </div>
        </div>
    );
};

export default CitationCard;
