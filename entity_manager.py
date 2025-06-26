from typing import List, Dict, Any
from entity import Entity

class EntityManager:
    """Manages all entities in the game"""
    
    def __init__(self):
        self.entities: List[Entity] = []
        self._entities_by_tag: Dict[int, List[Entity]] = {}
    
    def add_entity(self, entity: Entity):
        """Add an entity to the manager"""
        if entity not in self.entities:
            self.entities.append(entity)
            
            # Add to tag-based lookup
            if entity.tag not in self._entities_by_tag:
                self._entities_by_tag[entity.tag] = []
            self._entities_by_tag[entity.tag].append(entity)
    
    def remove_entity(self, entity: Entity):
        """Remove an entity from the manager"""
        if entity in self.entities:
            self.entities.remove(entity)
            
            # Remove from tag-based lookup
            if entity.tag in self._entities_by_tag:
                if entity in self._entities_by_tag[entity.tag]:
                    self._entities_by_tag[entity.tag].remove(entity)
    
    def get_entities_by_tag(self, tag: int) -> List[Entity]:
        """Get all entities with a specific tag"""
        return self._entities_by_tag.get(tag, [])
    
    def get_active_entities(self) -> List[Entity]:
        """Get all active entities"""
        return [entity for entity in self.entities if entity.is_active()]
    
    def update_all(self):
        """Update all active entities"""
        for entity in self.get_active_entities():
            entity.update()
    
    def draw_all(self, surface):
        """Draw all active entities"""
        for entity in self.get_active_entities():
            entity.draw(surface)
    
    def cleanup_inactive(self):
        """Remove all inactive entities"""
        inactive_entities = [entity for entity in self.entities if not entity.is_active()]
        for entity in inactive_entities:
            self.remove_entity(entity)
    
    def clear_all(self):
        """Remove all entities"""
        self.entities.clear()
        self._entities_by_tag.clear()
    
    def count_by_tag(self, tag: int) -> int:
        """Count entities with a specific tag"""
        return len(self.get_entities_by_tag(tag))
    
    def get_first_by_tag(self, tag: int) -> Entity | None:
        """Get the first entity with a specific tag"""
        entities = self.get_entities_by_tag(tag)
        return entities[0] if entities else None
