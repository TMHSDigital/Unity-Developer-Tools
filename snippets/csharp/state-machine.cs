// Finite State Machine
// Simple state machine for AI, game states, or player behavior.
// Each state is a separate class implementing IState.

using UnityEngine;

namespace MyGame
{
    public interface IState
    {
        void Enter();
        void Update();
        void FixedUpdate();
        void Exit();
    }

    public class StateMachine
    {
        private IState _currentState;

        public IState CurrentState => _currentState;

        public void ChangeState(IState newState)
        {
            _currentState?.Exit();
            _currentState = newState;
            _currentState?.Enter();
        }

        public void Update() => _currentState?.Update();
        public void FixedUpdate() => _currentState?.FixedUpdate();
    }

    // Example: Enemy idle state
    public class IdleState : IState
    {
        private readonly Transform _owner;
        private readonly Transform _player;
        private readonly float _detectionRange;
        private readonly StateMachine _sm;

        public IdleState(Transform owner, Transform player, float detectionRange, StateMachine sm)
        {
            _owner = owner;
            _player = player;
            _detectionRange = detectionRange;
            _sm = sm;
        }

        public void Enter() => Debug.Log("Entering Idle");

        public void Update()
        {
            float distance = Vector3.Distance(_owner.position, _player.position);
            if (distance < _detectionRange)
            {
                _sm.ChangeState(new ChaseState(_owner, _player, _detectionRange, _sm));
            }
        }

        public void FixedUpdate() { }
        public void Exit() => Debug.Log("Exiting Idle");
    }

    public class ChaseState : IState
    {
        private readonly Transform _owner;
        private readonly Transform _player;
        private readonly float _detectionRange;
        private readonly StateMachine _sm;

        public ChaseState(Transform owner, Transform player, float detectionRange, StateMachine sm)
        {
            _owner = owner;
            _player = player;
            _detectionRange = detectionRange;
            _sm = sm;
        }

        public void Enter() => Debug.Log("Entering Chase");

        public void Update()
        {
            float distance = Vector3.Distance(_owner.position, _player.position);
            if (distance > _detectionRange * 1.5f)
            {
                _sm.ChangeState(new IdleState(_owner, _player, _detectionRange, _sm));
            }
        }

        public void FixedUpdate()
        {
            Vector3 direction = (_player.position - _owner.position).normalized;
            _owner.position += direction * 3f * Time.fixedDeltaTime;
        }

        public void Exit() => Debug.Log("Exiting Chase");
    }
}
