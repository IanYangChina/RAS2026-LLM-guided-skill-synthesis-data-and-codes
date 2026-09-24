## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0851 | 0.34 | ❌ rejected |
| 9 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0597 | 0.31 | ❌ rejected |
| 8 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0898 | 0.33 | ❌ rejected |
| 7 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1336 | 0.47 | ✅ accepted |
| 6 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2102 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.085) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  weight: 0.7
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_grasp
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
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
  subtask_id: reach_object
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: approach_goal
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
    - 0.25
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: descend_to_goal
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.085
- **task_score** (E): 0.342
- **fitness_score**: 0.645  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1114 |
| descend_to_grasp | 1.00 | 1.00 | 0.1486 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2144 |
| transport_to_goal | 1.00 | 1.00 | 0.2357 |
| descend_to_goal | 1.00 | 1.00 | 0.1405 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_after_place | 1.00 | 1.00 | 0.0656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.194) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.194)→(0.492, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.045)→(0.484, 0.000, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 43.333 | 0.144 | 0.200 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.036)→(0.482, 0.000, 0.251) | (0.497, 0.000, 0.026)→(0.490, 0.000, 0.235) | 0.266→0.219 | 1.00 / 38.333 | 0.079 | 0.486 |
| transport_to_goal | approach | 1.00 / step_budget | (0.482, 0.000, 0.251)→(0.577, 0.174, 0.371) | (0.490, 0.000, 0.235)→(0.583, 0.175, 0.343) | 0.219→0.157 | 1.00 / 24.667 | 0.110 | 0.184 |
| descend_to_goal | approach | 1.00 / step_budget | (0.577, 0.174, 0.371)→(0.580, 0.183, 0.231) | (0.583, 0.175, 0.343)→(0.567, 0.186, 0.145) | 0.157→0.072 | 1.00 / 19.667 | 146985.605 | 0.968 |
| release_object | release | 1.00 / step_budget | (0.580, 0.183, 0.231)→(0.575, 0.181, 0.251) | (0.567, 0.186, 0.145)→(0.561, 0.184, 0.021) | 0.072→0.168 | 1.00 / 3.667 | 0.197 | 1.193 |
| retract_after_place | retract | 1.00 / step_budget | (0.575, 0.181, 0.251)→(0.580, 0.184, 0.317) | (0.561, 0.184, 0.021)→(0.557, 0.181, 0.026) | 0.168→0.163 | 1.00 / 4.000 | 0.123 | 0.198 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.426
- phase_score: 0.194
- phase_breakdown.reach_object_score: 0.067
- phase_breakdown.place_goal_score: 0.249
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.426
- **Median Q (composite search score)**: -0.091
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.438


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28065,"average_solve_count":310.0,"average_success_count":310.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.24506,"descend_to_goal.place_z":0.03945,"descend_to_goal.speed":0.056,"descend_to_grasp.descend_offset":0.01091,"descend_to_grasp.speed":0.10997,"grasp_object.max_duration":1.19439,"lift_object.lift_height":0.29544,"lift_object.speed":0.02866,"release_object.release_duration":0.81011,"retract_after_place.speed":0.195,"transport_to_goal.speed":0.06586},"optimized_scores":{"best_composite_score":-0.12184,"best_fitness_score":0.60816,"best_task_score":0.26953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.53784,0.14919,-0.00998],"force_p95":1.27169,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76648,"mean_force":0.54186,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5472,0.14826,0.28673]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50948,-0.02207,-0.00144],"force_p95":0.4928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51403,"mean_force":0.1803,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49943,-0.02236,0.03754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18441.0,"contact_point_centroid":[0.49743,-0.00316,0.17433],"force_p95":0.0772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30782,"mean_force":0.05378,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49719,-0.02229,0.17201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19064.0,"contact_point_centroid":[0.49736,-0.04139,0.17288],"force_p95":0.07615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28861,"mean_force":0.05253,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49718,-0.02229,0.1709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":890.0,"contact_point_centroid":[0.54921,0.16816,0.266],"force_p95":0.0994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18226,"mean_force":0.06065,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54969,0.14913,0.26683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00206],"force_p95":0.1401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1821,"mean_force":0.12737,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50166,-0.02241,0.0377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7599.0,"contact_point_centroid":[0.55034,0.16285,0.34379],"force_p95":0.09223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17367,"mean_force":0.05918,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.5499,0.14376,0.3421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1065.0,"contact_point_centroid":[0.54855,0.13023,0.26669],"force_p95":0.08796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17322,"mean_force":0.0523,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5497,0.14914,0.26685]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50338,-0.00924,0.24749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8547.0,"contact_point_centroid":[0.54993,0.12463,0.34341],"force_p95":0.08831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13427,"mean_force":0.0541,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.54991,0.14379,0.34161]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.53783,0.14925,-0.00221],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.134,"mean_force":0.11291,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54867,0.14925,0.32163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.50104,-0.00318,0.03919],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12914,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50049,-0.02239,0.03642]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.5072,-0.0209,0.11836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13090.0,"contact_point_centroid":[0.52309,0.03947,0.35867],"force_p95":0.06741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09622,"mean_force":0.04565,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52295,0.05856,0.35756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11566.0,"contact_point_centroid":[0.52372,0.07856,0.35968],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08811,"mean_force":0.05087,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5232,0.05935,0.35803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.50109,-0.04148,0.03825],"force_p95":0.06985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08151,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50049,-0.02239,0.03642]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53782,0.14924,0.02602],"final_tcp_position":[0.55139,0.15054,0.35229],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.76648,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50838,-0.01931,0.19322],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50867,-0.02257,0.04546],"tcp_start":[0.50838,-0.01931,0.19322],"tcp_to_object_dist_end":0.02008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02235,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26535,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13663,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.1821,"tcp_end":[0.50046,-0.02238,0.03639],"tcp_start":[0.50867,-0.02257,0.04546],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,-0.02223,0.29445],"object_pos_start":[0.5136,-0.02235,0.02579],"object_to_goal_dist_end":0.19443,"object_to_goal_dist_start":0.26535,"object_z_max":0.29418,"peak_contact_force":0.07795,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37589.0,"raw_peak_contact_force":0.51403,"tcp_end":[0.49826,-0.02232,0.31209],"tcp_start":[0.50046,-0.02238,0.03639],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.55446,0.13917,0.38667],"object_pos_start":[0.50594,-0.02223,0.29445],"object_to_goal_dist_end":0.16515,"object_to_goal_dist_start":0.19443,"object_z_max":0.38654,"peak_contact_force":0.08343,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24656.0,"raw_peak_contact_force":0.09622,"subtask_id":"place_goal","tcp_end":[0.54938,0.13903,0.40725],"tcp_start":[0.49826,-0.02232,0.31209],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.53876,0.14884,0.24739],"object_pos_start":[0.55446,0.13917,0.38667],"object_to_goal_dist_end":0.0298,"object_to_goal_dist_start":0.16515,"object_z_max":0.38667,"peak_contact_force":0.10106,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16146.0,"raw_peak_contact_force":0.17367,"subtask_id":"place_goal","tcp_end":[0.55117,0.1495,0.27051],"tcp_start":[0.54938,0.13903,0.40725],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53659,0.14771,0.01507],"object_pos_start":[0.53876,0.14884,0.24739],"object_to_goal_dist_end":0.20769,"object_to_goal_dist_start":0.0298,"object_z_max":0.24739,"peak_contact_force":0.12547,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2097.0,"raw_peak_contact_force":1.76648,"subtask_id":"place_goal","tcp_end":[0.54717,0.14826,0.29228],"tcp_start":[0.55117,0.1495,0.27051],"tcp_to_object_dist_end":0.27741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.53782,0.14924,0.02602],"object_pos_start":[0.53659,0.14771,0.01507],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.20769,"object_z_max":0.02677,"peak_contact_force":0.12266,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":876.0,"raw_peak_contact_force":0.134,"tcp_end":[0.55139,0.15054,0.35229],"tcp_start":[0.54717,0.14826,0.29228],"tcp_to_object_dist_end":0.32656,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62917,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.22182,"descend_to_goal.place_z":0.03947,"descend_to_goal.speed":0.10755,"descend_to_grasp.descend_offset":0.01005,"descend_to_grasp.speed":0.17349,"grasp_object.max_duration":1.40151,"lift_object.lift_height":0.18886,"lift_object.speed":0.028,"release_object.release_duration":1.3032,"retract_after_place.speed":0.1989,"transport_to_goal.speed":0.17386},"optimized_scores":{"best_composite_score":-0.04296,"best_fitness_score":0.68704,"best_task_score":0.42632},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.52939,0.23055,-0.00751],"force_p95":1.22845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68467,"mean_force":0.42166,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55555,0.23963,0.20817]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.49742,0.04286,-0.0016],"force_p95":0.44652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46327,"mean_force":0.2017,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48715,0.04316,0.03686]},{"body_a":"world","body_b":"grasp_target","contact_count":901.0,"contact_point_centroid":[0.52745,0.22849,-0.00214],"force_p95":0.2164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33768,"mean_force":0.12716,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.55754,0.24103,0.24762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":635.0,"contact_point_centroid":[0.55431,0.22239,0.1871],"force_p95":0.30491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33707,"mean_force":0.117,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55856,0.24117,0.19035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":669.0,"contact_point_centroid":[0.55554,0.25927,0.18602],"force_p95":0.26343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31507,"mean_force":0.10475,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5587,0.24124,0.19062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4631.0,"contact_point_centroid":[0.55962,0.25516,0.26202],"force_p95":0.12115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27202,"mean_force":0.07772,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55909,0.23723,0.26475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12962.0,"contact_point_centroid":[0.48417,0.06207,0.12056],"force_p95":0.07325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26765,"mean_force":0.04867,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48474,0.04294,0.11915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11709.0,"contact_point_centroid":[0.48439,0.02372,0.1165],"force_p95":0.07749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25561,"mean_force":0.05227,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48473,0.04294,0.11439]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04476,-0.00215],"force_p95":0.16739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2384,"mean_force":0.13428,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48946,0.04338,0.03717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3924.0,"contact_point_centroid":[0.55981,0.21824,0.26521],"force_p95":0.16132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22151,"mean_force":0.10463,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55905,0.23707,0.26744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10118.0,"contact_point_centroid":[0.5222,0.15246,0.26457],"force_p95":0.10058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18667,"mean_force":0.06729,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51888,0.13367,0.26358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9474.0,"contact_point_centroid":[0.52255,0.11582,0.26577],"force_p95":0.10718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18078,"mean_force":0.06979,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51928,0.13467,0.26426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3880.0,"contact_point_centroid":[0.48916,0.02402,0.03887],"force_p95":0.08556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1562,"mean_force":0.05444,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48831,0.04328,0.03595]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49831,0.0182,0.24709]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49588,0.04087,0.11776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.48823,0.06239,0.0384],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08147,"mean_force":0.04147,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48832,0.04328,0.03595]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52598,0.22768,0.02602],"final_tcp_position":[0.56083,0.24291,0.27724],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49786,0.03794,0.19273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49636,0.044,0.0446],"tcp_start":[0.49786,0.03794,0.19273],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04347,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24347,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15878,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11087.0,"raw_peak_contact_force":0.2384,"tcp_end":[0.48828,0.04327,0.03592],"tcp_start":[0.49636,0.044,0.0446],"tcp_to_object_dist_end":0.01655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.49441,0.04282,0.19099],"object_pos_start":[0.50113,0.04347,0.02548],"object_to_goal_dist_end":0.21835,"object_to_goal_dist_start":0.24347,"object_z_max":0.19071,"peak_contact_force":0.0801,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24767.0,"raw_peak_contact_force":0.46327,"tcp_end":[0.48508,0.04297,0.20516],"tcp_start":[0.48828,0.04327,0.03592],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.56632,0.23377,0.30246],"object_pos_start":[0.49441,0.04282,0.19099],"object_to_goal_dist_end":0.15609,"object_to_goal_dist_start":0.21835,"object_z_max":0.30234,"peak_contact_force":0.09977,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19592.0,"raw_peak_contact_force":0.18667,"subtask_id":"place_goal","tcp_end":[0.55872,0.23338,0.33175],"tcp_start":[0.48508,0.04297,0.20516],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.55324,0.24078,0.16182],"object_pos_start":[0.56632,0.23377,0.30246],"object_to_goal_dist_end":0.01918,"object_to_goal_dist_start":0.15609,"object_z_max":0.30247,"peak_contact_force":167951.73011,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8555.0,"raw_peak_contact_force":0.27202,"subtask_id":"place_goal","tcp_end":[0.56069,0.24209,0.19492],"tcp_start":[0.55872,0.23338,0.33175],"tcp_to_object_dist_end":0.03396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53783,0.23642,0.02043],"object_pos_start":[0.55324,0.24078,0.16182],"object_to_goal_dist_end":0.12939,"object_to_goal_dist_start":0.01918,"object_z_max":0.16182,"peak_contact_force":0.34428,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1465.0,"raw_peak_contact_force":1.68467,"subtask_id":"place_goal","tcp_end":[0.5555,0.23962,0.21546],"tcp_start":[0.56069,0.24209,0.19492],"tcp_to_object_dist_end":0.19585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.52598,0.22768,0.02602],"object_pos_start":[0.53783,0.23642,0.02043],"object_to_goal_dist_end":0.12788,"object_to_goal_dist_start":0.12939,"object_z_max":0.02742,"peak_contact_force":0.12302,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":901.0,"raw_peak_contact_force":0.33768,"tcp_end":[0.56083,0.24291,0.27724],"tcp_start":[0.5555,0.23962,0.21546],"tcp_to_object_dist_end":0.25408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4854,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.28686,"descend_to_goal.place_z":0.02832,"descend_to_goal.speed":0.08876,"descend_to_grasp.descend_offset":0.01005,"descend_to_grasp.speed":0.08114,"grasp_object.max_duration":0.5635,"lift_object.lift_height":0.21769,"lift_object.speed":0.03933,"release_object.release_duration":1.26203,"retract_after_place.speed":0.05263,"transport_to_goal.speed":0.22658},"optimized_scores":{"best_composite_score":-0.09052,"best_fitness_score":0.63948,"best_task_score":0.33106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":777.0,"contact_point_centroid":[0.60849,0.16957,-0.00414],"force_p95":0.89853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45766,"mean_force":0.21764,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.62593,0.15524,0.26832]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.47215,-0.01964,-0.00145],"force_p95":0.46524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48215,"mean_force":0.19891,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46311,-0.01955,0.03818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.62569,0.13341,0.36324],"force_p95":0.24226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33428,"mean_force":0.1398,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.62301,0.15124,0.36826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":577.0,"contact_point_centroid":[0.62469,0.16813,0.35874],"force_p95":0.18589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28758,"mean_force":0.09866,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.62304,0.15129,0.3636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11676.0,"contact_point_centroid":[0.53572,0.03979,0.29885],"force_p95":0.11688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26969,"mean_force":0.06325,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53447,0.05885,0.29765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13324.0,"contact_point_centroid":[0.53811,0.08059,0.30103],"force_p95":0.10146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2677,"mean_force":0.05567,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53713,0.06167,0.29994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13486.0,"contact_point_centroid":[0.46087,-0.0386,0.13843],"force_p95":0.07438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26544,"mean_force":0.05141,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46077,-0.01947,0.13649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13056.0,"contact_point_centroid":[0.46093,-0.00032,0.13592],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26324,"mean_force":0.05266,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46076,-0.01947,0.13382]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02007,-0.00205],"force_p95":0.1377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17883,"mean_force":0.12675,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46522,-0.0196,0.03829]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48844,-0.00799,0.24844]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60816,0.16695,-0.00199],"force_p95":0.12541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12813,"mean_force":0.12264,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6239,0.15622,0.22665]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.60816,0.16696,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62491,0.15676,0.28239]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47326,-0.01821,0.11906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46379,-0.00035,0.03974],"force_p95":0.06603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10261,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01957,0.0372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.46404,-0.03882,0.03917],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0849,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01957,0.0372]},{"body_a":"left_finger","body_b":"right_finger","contact_count":822.0,"contact_point_centroid":[0.62639,0.15542,0.26718],"force_p95":0.01277,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01073,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.62606,0.15541,0.26485]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60816,0.16696,0.02602],"final_tcp_position":[0.62871,0.15815,0.32024],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.98314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47709,-0.01677,0.19456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47186,-0.01975,0.04499],"tcp_start":[0.47709,-0.01677,0.19456],"tcp_to_object_dist_end":0.01946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01969,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13582,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12028.0,"raw_peak_contact_force":0.17883,"tcp_end":[0.46409,-0.01957,0.03717],"tcp_start":[0.47186,-0.01975,0.04499],"tcp_to_object_dist_end":0.01651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.46954,-0.01928,0.21987],"object_pos_start":[0.47606,-0.01969,0.02581],"object_to_goal_dist_end":0.24279,"object_to_goal_dist_start":0.28827,"object_z_max":0.21959,"peak_contact_force":0.07795,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26627.0,"raw_peak_contact_force":0.48215,"tcp_end":[0.46122,-0.01948,0.2353],"tcp_start":[0.46409,-0.01957,0.03717],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.62812,0.15155,0.33917],"object_pos_start":[0.46954,-0.01928,0.21987],"object_to_goal_dist_end":0.14939,"object_to_goal_dist_start":0.24279,"object_z_max":0.33907,"peak_contact_force":0.14643,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25000.0,"raw_peak_contact_force":0.26969,"subtask_id":"place_goal","tcp_end":[0.62298,0.15073,0.37426],"tcp_start":[0.46122,-0.01948,0.2353],"tcp_to_object_dist_end":0.03548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.60818,0.16711,0.02603],"object_pos_start":[0.62812,0.15155,0.33917],"object_to_goal_dist_end":0.16582,"object_to_goal_dist_start":0.14939,"object_z_max":0.33917,"peak_contact_force":273004.98314,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2422.0,"raw_peak_contact_force":2.45766,"subtask_id":"place_goal","tcp_end":[0.62754,0.15732,0.22718],"tcp_start":[0.62298,0.15073,0.37426],"tcp_to_object_dist_end":0.20232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60816,0.16696,0.02602],"object_pos_start":[0.60818,0.16711,0.02603],"object_to_goal_dist_end":0.16582,"object_to_goal_dist_start":0.16582,"object_z_max":0.02603,"peak_contact_force":0.12266,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1035.0,"raw_peak_contact_force":0.12813,"subtask_id":"place_goal","tcp_end":[0.62268,0.1558,0.246],"tcp_start":[0.62754,0.15732,0.22718],"tcp_to_object_dist_end":0.22075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.60816,0.16696,0.02602],"object_pos_start":[0.60816,0.16696,0.02602],"object_to_goal_dist_end":0.16582,"object_to_goal_dist_start":0.16582,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.12266,"tcp_end":[0.62871,0.15815,0.32024],"tcp_start":[0.62268,0.1558,0.246],"tcp_to_object_dist_end":0.29507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```