## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 4 | 0.6785 | 0.88 | ❌ rejected |
| 5 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5985 | 0.88 | ✅ accepted |
| 4 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 5 | 0.0428 | 0.29 | ❌ rejected |
| 3 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 4 | 0.6785 | 0.88 | ✅ accepted |
| 2 | insert → insert → approach → push → retract → lift → insert → push | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.5800 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: obstacle_reach
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.678) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: reach_high
  offset:
  - 0.0
  - 0.0
  - 0.4
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_high
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.4
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.2
      - 0.5
      default: 0.4
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_high
- id: align_over_goal
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.4
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_high
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.4], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **align_over_goal** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.4], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.678
- **task_score** (E): 0.878
- **fitness_score**: 0.878  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.33 | 0.00 | 0.3417 |
| descend_to_goal | 1.00 | 0.00 | 0.3273 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.33 / step_budget | (0.350, -0.000, 0.321)→(0.644, 0.000, 0.492) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_goal | descend | 1.00 / step_budget | (0.644, 0.000, 0.492)→(0.690, 0.000, 0.168) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.715
- path_efficiency: 0.550
- arc_smoothness: 0.994
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.879
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.879
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.879
- **Median Q (composite search score)**: 0.678
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `30565d16bb12c763ef96950bff0806542e706772a2f5d6530b71a1e799295889`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `93ed75540af82fc2f732261ad21f1d84d6fc60a0bcf806dd0394bfdc69d4362f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.01449,"average_mean_iterations":8.02899,"average_solve_count":69.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.28371,"approach_high.arc_height":0.29515,"approach_high.speed":0.32215,"descend_to_goal.descent_speed":0.15358},"optimized_scores":{"best_composite_score":0.67856,"best_fitness_score":0.87856,"best_task_score":0.87856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01942,"key_states":{"actual_goal_position":[0.7137,-0.02302,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70672,-0.02276,0.16812],"realised_goal_position":[0.7137,-0.02302,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":332.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.65839,-0.0192,0.47417],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.81159,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.70672,-0.02276,0.16812],"tcp_start":[0.65839,-0.0192,0.47417],"tcp_to_object_dist_end":0.7268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e2f42f3fbbcca284b57f515aa7c9c12d3405e5434d2b225f750641c72d8a7bd9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.01235,"average_mean_iterations":6.95062,"average_solve_count":81.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.30997,"approach_high.arc_height":0.39392,"approach_high.speed":0.2522,"descend_to_goal.descent_speed":0.14028},"optimized_scores":{"best_composite_score":0.67841,"best_fitness_score":0.87841,"best_task_score":0.87841},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01945,"key_states":{"actual_goal_position":[0.70118,0.04505,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69399,0.04409,0.16804],"realised_goal_position":[0.70118,0.04505,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":321.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.64237,0.03681,0.4807],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.80316,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.69399,0.04409,0.16804],"tcp_start":[0.64237,0.03681,0.4807],"tcp_to_object_dist_end":0.71541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6daafe4988ca0b57abfa37034ad4d1d5846eda9319b3f27d8d423c2e135ec43b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1875,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.35058,"approach_high.arc_height":0.29824,"approach_high.speed":0.39731,"descend_to_goal.descent_speed":0.17612},"optimized_scores":{"best_composite_score":0.67841,"best_fitness_score":0.87841,"best_task_score":0.87841},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01945,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67042,-0.01998,0.16858],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":327.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_high","tcp_end":[0.63116,-0.01706,0.52132],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.8188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.67042,-0.01998,0.16858],"tcp_start":[0.63116,-0.01706,0.52132],"tcp_to_object_dist_end":0.69157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```