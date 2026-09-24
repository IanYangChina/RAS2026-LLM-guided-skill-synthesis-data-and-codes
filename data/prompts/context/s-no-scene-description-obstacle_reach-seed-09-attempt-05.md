## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → approach | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1800 | 0.00 | ❌ rejected |
| 4 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 3 | 0.7338 | 0.88 | ❌ rejected |
| 3 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | -0.1000 | 0.00 | ❌ rejected |
| 2 | approach → descend → approach | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7159 | 0.90 | ✅ accepted |
| 1 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | 0.7943 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.180) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: reach_above_goal
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_goal
- id: descend_to_approach
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: descent_near_goal
    when: after_phase
    predicate: pose_within_tolerance
    args:
      tolerance: 0.02
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_above_goal
- id: final_precise_approach
  type: approach
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    final_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: final_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    args:
      tolerance: 0.02
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_approach** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descent_near_goal, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02, args={'tolerance': 0.02}
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **final_precise_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - final_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=final_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02, args={'tolerance': 0.02}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]

## Design Metrics

- **Composite score**: -0.180
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.00 | 0.33 | 0.2099 |
| descend_to_fine | 0.00 | 0.33 | 0.0049 |
| final_precise_approach | 0.00 | 0.00 | 0.0020 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.00 / step_budget | (0.350, -0.000, 0.321)→(0.556, -0.013, 0.319) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.33 / 0.333 | 74.792 | 443.769 | link7 ↔ obstacle_block/obstacle_block_geom |
| descend_to_fine | descend | 0.00 / step_budget | (0.604, -0.024, 0.297)→(0.607, -0.025, 0.294) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.33 / 0.333 | 0.000 | 604.865 | link5 ↔ obstacle_block/obstacle_block_geom |
| final_precise_approach | approach | 0.00 / step_budget | (0.617, -0.026, 0.277)→(0.617, -0.026, 0.275) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 | — |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.870
- path_efficiency: 0.822
- arc_smoothness: 0.981
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 400.506 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.134
- min_tcp_distance: 0.134
- tcp_proximity_score: 0.409
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link7
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.180
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4a44882555f0d0b14e6aa599db443a998da24652eb9b9e2830cc337dec76aa35`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `47104ba1d83b6713840746a9744b8461d7698be90a7b9bbdb4a5ee2c9b597658`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":125.0,"average_failure_rate":0.67568,"average_mean_iterations":136.5027,"average_solve_count":185.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.25967,"descend_to_fine.descend_speed":0.16508,"final_precise_approach.final_speed":0.04741},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":465.0,"contact_point_centroid":[0.47043,-0.00858,0.2999],"force_p95":307.20577,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":400.50611,"mean_force":261.21867,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44048,-0.00569,0.33143]},{"body_a":"obstacle_block","body_b":"link6","contact_count":145.0,"contact_point_centroid":[0.53853,-0.01232,0.29986],"force_p95":260.17237,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":304.99153,"mean_force":210.81744,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.47692,-0.00869,0.35427]}],"total_contact_groups":2},"final_pose_error":0.13393,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.64311,-0.01854,0.24545],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":400.50611,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":400.50611,"phase_type":"approach","raw_contact_event_count":610.0,"raw_peak_contact_force":400.50611,"subtask_id":"reach_above_goal","tcp_end":[0.60719,-0.01732,0.27741],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.66778,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":8.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_fine","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.62057,-0.01781,0.26595],"tcp_start":[0.61415,-0.01759,0.27146],"tcp_to_object_dist_end":0.6754,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"final_precise_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.64311,-0.01854,0.24545],"tcp_start":[0.64233,-0.0185,0.24739],"tcp_to_object_dist_end":0.6886,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `dd76534a039a46a09f9e3c15723c51c6f1027acc2aa2ab4b06e8dae86dbdcd96`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":129.0,"average_failure_rate":0.72472,"average_mean_iterations":146.69663,"average_solve_count":178.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.30027,"descend_to_fine.descend_speed":0.17628,"final_precise_approach.final_speed":0.06901},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.47224,-0.01067,0.29989],"force_p95":309.89777,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":430.81145,"mean_force":257.75299,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44208,-0.00783,0.33163]},{"body_a":"obstacle_block","body_b":"link6","contact_count":107.0,"contact_point_centroid":[0.53849,-0.01591,0.29986],"force_p95":260.81581,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":304.97813,"mean_force":208.9984,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.47768,-0.01191,0.3536]}],"total_contact_groups":2},"final_pose_error":0.19477,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.59758,-0.02637,0.27655],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":430.81145,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":744.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_high","phase_peak_obstacle_force":430.81145,"phase_type":"approach","raw_contact_event_count":521.0,"raw_peak_contact_force":430.81145,"subtask_id":"reach_above_goal","tcp_end":[0.57027,-0.02104,0.31673],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.65266,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":18.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_fine","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.59023,-0.02534,0.29548],"tcp_start":[0.58786,-0.02389,0.29917],"tcp_to_object_dist_end":0.66055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"final_precise_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.59758,-0.02637,0.27655],"tcp_start":[0.59728,-0.0263,0.27767],"tcp_to_object_dist_end":0.659,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b9c2919c979234936a5d994fa5db826639b75dec9196808e9cc353d4e638017c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":154.0,"average_failure_rate":0.63115,"average_mean_iterations":129.07787,"average_solve_count":244.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.24442,"descend_to_fine.descend_speed":0.09409,"final_precise_approach.final_speed":0.03747},"optimized_scores":{"best_composite_score":-0.18,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":134.0,"contact_point_centroid":[0.53931,0.09215,0.29857],"force_p95":703.23439,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":1814.59368,"mean_force":293.79617,"phase_index":1.0,"phase_name":"descend_to_fine","phase_type":"descend","tcp_position_centroid":[0.59527,-0.01205,0.27211]},{"body_a":"obstacle_block","body_b":"link7","contact_count":445.0,"contact_point_centroid":[0.46193,-0.00269,0.29988],"force_p95":314.52022,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":499.98811,"mean_force":277.3415,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4294,3e-05,0.32814]},{"body_a":"obstacle_block","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.53996,0.0009,0.29993],"force_p95":319.04603,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":361.72161,"mean_force":283.69281,"phase_index":1.0,"phase_name":"descend_to_fine","phase_type":"descend","tcp_position_centroid":[0.53215,0.00021,0.35433]},{"body_a":"obstacle_block","body_b":"link6","contact_count":135.0,"contact_point_centroid":[0.53866,-0.00236,0.29989],"force_p95":280.92535,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":311.8201,"mean_force":252.40678,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.47299,0.00019,0.355]},{"body_a":"obstacle_block","body_b":"link6","contact_count":204.0,"contact_point_centroid":[0.53997,-0.00124,0.29993],"force_p95":236.9794,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":299.14997,"mean_force":165.29241,"phase_index":1.0,"phase_name":"descend_to_fine","phase_type":"descend","tcp_position_centroid":[0.50469,0.00041,0.36586]},{"body_a":"obstacle_block","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.53996,0.09026,0.29988],"force_p95":0.0,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"final_precise_approach","phase_type":"approach","tcp_position_centroid":[0.60972,-0.03072,0.32196]}],"total_contact_groups":6},"final_pose_error":0.1658,"key_states":{"actual_goal_position":[0.66286,-7e-05,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.61071,-0.03364,0.30377],"realised_goal_position":[0.66286,-7e-05,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":1814.59368,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":737.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":224.37648,"phase_name":"approach_high","phase_peak_obstacle_force":499.98811,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":499.98811,"subtask_id":"reach_above_goal","tcp_end":[0.49138,0.00031,0.36386],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.61144,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_fine","phase_peak_obstacle_force":1814.59368,"phase_type":"descend","raw_contact_event_count":624.0,"raw_peak_contact_force":1814.59368,"subtask_id":"reach_above_goal","tcp_end":[0.60967,-0.03058,0.32186],"tcp_start":[0.60926,-0.02952,0.32053],"tcp_to_object_dist_end":0.69009,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"final_precise_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.61071,-0.03364,0.30377],"tcp_start":[0.61073,-0.03319,0.30636],"tcp_to_object_dist_end":0.68291,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```